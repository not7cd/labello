import logging
import os
from datetime import datetime

from flask import (
    Flask,
    flash,
    render_template,
    redirect,
    url_for,
    request,
    jsonify,
    abort,
    send_file,
)

from labello import settings
from labello.database import db, Label
from labello.templating.loader import jinja_env as label_tpl, get_variables
from labello.templating import epl
from labello.rendering.epl import Renderer
from labello.printer import printer
from labello.api import api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="web/templates")
app.config.from_object("labello.settings")
app.register_blueprint(api, url_prefix="/api")

common_vars_tpl = {"app": app.config.get_namespace("APP_")}


@app.before_request
def before_request():
    app.logger.debug("connecting to db")
    db.connect()
    common_vars_tpl["printer_status"] = printer.get_status()
    common_vars_tpl["printer_state"] = printer.get_state()


@app.teardown_appcontext
def after_request(error):
    app.logger.debug("closing db")
    db.close()


@app.route("/")
def gallery():
    labels = Label.select()
    return render_template("label_gallery.html", labels=labels, **common_vars_tpl)


@app.route("/editor/new", methods=["GET", "POST"])
@app.route("/editor/<label_id>", methods=["GET", "POST"])
def label_editor(label_id=None):
    """Edit or create labels"""
    if request.method == "POST" and request.values.get("raw"):
        app.logger.info(request.values)
        data = request.values.get("raw")
        name = request.values.get("label_name")

        if request.values.get("print"):
            res = printer.send_raw(data)
            flash(
                f"sent {len(data)} bytes to printer",
                "success" if res == 0 else "error",
            )
        elif request.values.get("save"):
            if label_id is None:
                new_label = Label.create(raw=data, last_edit=datetime.now(), name=name)
                new_label.save()
                flash(
                    f"New label created {new_label.name}",
                    "success" if new_label else "error",
                )
                return redirect(url_for("label_editor", label_id=new_label.id))
            else:
                label = Label.select().where(Label.id == label_id).get()
                label.raw = data
                label.name = name
                label.last_edit = datetime.now()
                label.save()
                flash(f"Congrats, you managed to edit this label ;)", "info")

    if label_id:
        label = Label.select().where(Label.id == label_id).get()
        if label:
            return render_template(
                "editor.html",
                raw=label.raw,
                label_id=label_id,
                name=label.name,
                **common_vars_tpl,
            )
    return render_template("editor.html", raw="", label_id=label_id, **common_vars_tpl)


def sub_dict(somedict, somekeys, default=None):
    return dict([(k, somedict.get(k, default)) for k in somekeys])


@app.route("/print/<label_id>", methods=["GET", "POST"])
def print_template(label_id):
    try:
        label_vars = get_variables(label_tpl, label_id)
    except Exception as exc:
        logger.error(exc)
        flash(
            f"Error loading label {label_id} {exc}", "error",
        )
        label_vars = {}

    if request.method == "POST":
        label_ctx = sub_dict(request.form, label_vars, default="")
    else:
        label_ctx = sub_dict(request.values, label_vars, default="")

    try:
        template = label_tpl.loader.load(label_tpl, label_id)
        # TODO: why are we not inhereting globals from jinja_env? fix this
        template.globals.update(epl=epl)
        rendered = template.render(label_ctx)
    except Exception as exc:
        logger.error(exc)
        flash(
            f"Error rendering {exc}", "error",
        )
        rendered = None

    if request.method == "POST" and request.values.get("preview"):
        print(label_ctx)
        return redirect(url_for("print_template", label_id=label_id, **label_ctx))

    if request.method == "POST" and request.values.get("print"):
        data = rendered
        res = printer.send_raw(data)
        flash(
            f"sent {len(data)} bytes to printer",
            "success" if res == 0 else "error",
        )
    return render_template(
        "print.html",
        rendered=rendered,
        label_id=label_id,
        label_vars=label_ctx,
        **common_vars_tpl,
    )


@app.route("/send_raw", methods=["GET", "POST"])
def send_raw():
    """Send raw text to printer"""
    if request.method == "POST" and request.values.get("raw"):
        data = request.values.get("raw")
        res = printer.send_raw(data)
        flash(
            f"sent {len(data)} bytes to printer",
            "success" if res == 0 else "error",
        )

    return render_template(
        "send_raw.html", printer_name=settings.printer_name, **common_vars_tpl
    )


@app.route("/fork/<label_id>", methods=["GET", "POST"])
def fork_label(label_id):
    """fork existing label"""
    label = Label.select().where(Label.id == label_id).get()
    new_label = Label.create(
        raw=label.raw, last_edit=datetime.now(), name="Copy of {}".format(label.name)
    )
    new_label.save()
    flash(
        f"Label forked {new_label.name}", "success" if new_label else "error",
    )
    return redirect(url_for("label_editor", label_id=new_label.id))


@app.route("/delete/<label_id>", methods=["GET", "POST"])
def delete_label(label_id):
    """delete existing label"""
    if label_id in app.config.get("labels", {}).get("protected", []):
        abort(401)
    label = Label.select().where(Label.id == label_id).get()
    label.delete_instance()
    flash(
        f"Deleted {label.name}", "success" if label else "error",
    )
    return redirect(url_for("gallery"))


r = Renderer()


@app.route("/api/render/<label_id>.png", methods=["GET"])
def render_label(label_id):
    label = Label.select().where(Label.id == label_id)
    if label:
        label = label.get()
    else:
        return abort(404)

    img = r.render(label.raw)
    img_path = "label_{}.png".format(label_id)
    img.save(app.config["APP_IMAGES_PATH"] + img_path)
    return send_file(
        "." + app.config["APP_IMAGES_PATH"] + img_path,
        mimetype="image/png",
        attachment_filename=img_path,
    )
