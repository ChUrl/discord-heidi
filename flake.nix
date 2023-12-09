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
          overlays = [ devshell.overlays.default ];
        };

        myPython = pkgs.python311.withPackages (p: with p; [
          # Basic
          rich

          # Discord
          discordpy
          python-dotenv
          pynacl

          # Scraping
          # beautifulsoup4
          # requests

          # MachineLearning
          # torch-rocm
          # torchvision-rocm
          # numpy
          # matplotlib
          # nltk
        ]);
      in {
        devShell = pkgs.devshell.mkShell {
          name = "HeidiBot";

          packages = with pkgs; [
            myPython
            # nodePackages.pyright # LSP
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
