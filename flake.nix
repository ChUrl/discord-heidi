{
  description = "";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.devshell.url = "github:numtide/devshell";

  outputs = { self, nixpkgs, flake-utils, devshell }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
          overlays = [ devshell.overlay ];
        };

        myPython = pkgs.python310.withPackages (p: with p; [
          yt-dlp
        ]);
      in {
        devShell = pkgs.devshell.mkShell {
          name = "";

          packages = with pkgs; [
            myPython
          ];

          # Use $1 for positional args
          commands = [
            # {
            #   name = "";
            #   help = "";
            #   command = "";
            # }
          ];
        };
      });
}
