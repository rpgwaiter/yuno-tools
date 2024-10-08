{
  description = "Tools relating to YU-NO";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.05";
  };

  outputs = {
    self,
    nixpkgs,
    ...
  } @ inputs: let
    system = "x86_64-linux"; # your version
    pkgs = nixpkgs.legacyPackages.${system};
  in {
    packages.${system} = {
      yunolzss = pkgs.stdenv.mkDerivation {
        name = "yunolzss";

        src = ./c;

        # Use $CC as it allows for stdenv to reference the correct C compiler
        buildPhase = ''
          $CC -c yunolzss.c -o yunolzss.so
        '';

        installPhase = ''
          mkdir -p $out/share
          cp yunolzss.so  $out/share/yunolzss.so
        '';
      };
    };
  };
}
