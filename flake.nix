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

        # TODO: Originally it was nixpkgs.fetchurl but that didn't work, pkgs.fetchurl did...
        #       Determine the difference between nixpkgs and pkgs

        # Taken from: https://github.com/gbtb/nix-stable-diffusion/blob/master/flake.nix
        # Overlay: https://nixos.wiki/wiki/Overlays
        # FetchURL: https://ryantm.github.io/nixpkgs/builders/fetchers/
        torch-rocm = pkgs.hiPrio (pkgs.python310Packages.torch-bin.overrideAttrs (old: {
          src = pkgs.fetchurl {
            name = "torch-1.12.1+rocm5.1.1-cp310-cp310-linux_x86_64.whl";
            url = "https://download.pytorch.org/whl/rocm5.1.1/torch-1.12.1%2Brocm5.1.1-cp310-cp310-linux_x86_64.whl";
            hash = "sha256-kNShDx88BZjRQhWgnsaJAT8hXnStVMU1ugPNMEJcgnA=";
          };
        }));
        torchvision-rocm = pkgs.hiPrio (pkgs.python310Packages.torchvision-bin.overrideAttrs (old: {
          src = pkgs.fetchurl {
            name = "torchvision-0.13.1+rocm5.1.1-cp310-cp310-linux_x86_64.whl";
            url = "https://download.pytorch.org/whl/rocm5.1.1/torchvision-0.13.1%2Brocm5.1.1-cp310-cp310-linux_x86_64.whl";
            hash = "sha256-mYk4+XNXU6rjpgWfKUDq+5fH/HNPQ5wkEtAgJUDN/Jg=";
          };
        }));

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
