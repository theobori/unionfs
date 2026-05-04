{
  lib,
  buildPythonPackage,
  hatch,
  pytestCheckHook,
  msgpack,
  mfusepy,
}:
buildPythonPackage {
  pname = "unionfs";
  version = "1.0.0";
  pyproject = true;

  src = ./.;

  build-system = [
    hatch
  ];

  dependencies = [
    msgpack
    mfusepy
  ];

  nativeCheckInputs = [ pytestCheckHook ];

  pythonImportsCheck = [ "unionfs" ];

  meta = {
    description = "";
    homepage = "https://github.com/theobori/unionfs";
    license = lib.licenses.mit;
  };
}
