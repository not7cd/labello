{
  description = "A Nix-based development environment for labello";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python310
            poetry
            openssl
            
            # Dependencies for Pillow and other Python libs
            libjpeg
            zlib
            libpng
            freetype
            pkg-config
          ];

          shellHook = ''
            echo "Welcome to the labello development environment!"
            export POETRY_VIRTUALENVS_IN_PROJECT=1
            
            # Use Python 3.10 for Poetry
            export PYTHON="${pkgs.python310}/bin/python"
            if [ ! -d .venv ]; then
              poetry env use ${pkgs.python310}/bin/python
            fi

            if [ -t 0 ]; then
              echo "Python version: $(python --version)"
              echo "Poetry version: $(poetry --version)"
              echo "To get started:"
              echo "  1. poetry install"
              echo "  2. source env.sh"
              echo "  3. poetry run python helpers/db_create.py"
              echo "  4. poetry run python -m labello"
            fi
          '';
        };
      }
    );
}
