with (import <nixpkgs> {});
let
  my-python-packages = python-packages: with python-packages; [
    pip
    virtualenv
  ];
  python-with-my-packages = python311.withPackages my-python-packages;
in
mkShell {
  buildInputs = [
    python-with-my-packages
  ];
}
