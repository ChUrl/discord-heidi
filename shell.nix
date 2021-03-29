{ pkgs ? import <nixpkgs> {} }:

with pkgs;

let myPython = python38.buildEnv.override {
      extraLibs = with python38Packages; [
        python-dotenv
        rich
        discordpy
        beautifulsoup4
        selenium
      ];
    };
in

mkShell {
  buildInputs = [
    myPython
    nodePackages.pyright
    geckodriver
  ];
}
