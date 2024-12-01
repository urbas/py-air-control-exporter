{
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachSystem [ "x86_64-linux" "aarch64-linux" ] (system:
      with nixpkgs.legacyPackages.${system};
      let
        pyproject = builtins.fromTOML (builtins.readFile ./pyproject.toml);

        pkg = python3.pkgs.buildPythonPackage rec {
          pname = pyproject.project.name;
          version = pyproject.project.version;
          format = "pyproject";
          src = self;

          nativeBuildInputs = with python3.pkgs; [ hatchling ];

          propagatedBuildInputs = with python3.pkgs; [
            aiocoap
            click
            flask
            prometheus-client
            py-air-control
            pyyaml
          ];

          installCheckInputs = with python3.pkgs; [
            freezegun
            pytestCheckHook
            pytest-mock
          ];
        };

        editablePkg = pkg.overrideAttrs (oldAttrs: {
          nativeBuildInputs = oldAttrs.nativeBuildInputs ++ [
            (python3.pkgs.mkPythonEditablePackage {
              pname = pyproject.project.name;
              inherit (pyproject.project) scripts version;
              root = "$PWD";
            })
          ];
        });

      in {
        packages.default = pkg;
        devShells.default = mkShell {
          packages = with python3.pkgs; [
            ipython
            nixfmt
            pip
            pyright
            pytest
            pytest-cov
            pytest-mock
            ruff
            twine
            types-pyyaml
          ];
          inputsFrom = [ editablePkg ];
        };
      });
}
