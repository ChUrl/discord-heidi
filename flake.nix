{
  description = "HeidiBot for Discord";

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
          discordpy
          python-dotenv
          beautifulsoup4
          requests
          pynacl
          rich
          torch
          numpy
          nltk
        ]);
      in {
        devShell = pkgs.devshell.mkShell {
          name = "HeidiBot";

          packages = with pkgs; [
            myPython
            nodePackages.pyright # LSP
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
