{ ... }:
{
  projectRootFile = "flake.nix";
  programs.ruff-format.enable = true;
  programs.nixfmt.enable = true;
}
