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
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
  in {
    packages.${system} = rec {
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

      yuno-scripts = pkgs.python3Packages.buildPythonApplication rec {
        pname = "yuno-scripts";
        version = "0.6.0";
        format = "other";

        propagatedBuildInputs = [
          yunolzss
          pkgs.makeWrapper
        ];

        dontUnpack = true;
        installPhase = ''
          install -Dm755 ${./py/arcrepack.py} $out/bin/arcrepack
          install -Dm755 ${./py/arcunpack.py} $out/bin/arcunpack
          install -Dm755 ${./py/bmp2gp8.py} $out/bin/bmp2gp8
          install -Dm755 ${./py/gp82bmp.py} $out/bin/gp82bmp

          wrapProgram "$out/bin/arcrepack" --set YUNO_NATIVE_LIB ${yunolzss}/share/yunolzss.so
          wrapProgram "$out/bin/arcunpack" --set YUNO_NATIVE_LIB ${yunolzss}/share/yunolzss.so
          wrapProgram "$out/bin/bmp2gp8" --set YUNO_NATIVE_LIB ${yunolzss}/share/yunolzss.so
          wrapProgram "$out/bin/gp82bmp" --set YUNO_NATIVE_LIB ${yunolzss}/share/yunolzss.so
        '';
      };
    };
  };
}
