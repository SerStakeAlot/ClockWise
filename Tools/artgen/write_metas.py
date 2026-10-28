"""Generate Unity .meta files for Assets/Art and Assets/Editor.

Deterministic GUIDs (md5 of the project-relative path) so re-running never
churns the repo. Pixel-art import settings baked into texture metas.
"""
import hashlib
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

FOLDER_META = """fileFormatVersion: 2
guid: {guid}
folderAsset: yes
DefaultImporter:
  externalObjects: {{}}
  userData:
  assetBundleName:
  assetBundleVariant:
"""

SCRIPT_META = """fileFormatVersion: 2
guid: {guid}
MonoImporter:
  externalObjects: {{}}
  serializedVersion: 2
  defaultReferences: []
  executionOrder: 0
  icon: {{instanceID: 0}}
  userData:
  assetBundleName:
  assetBundleVariant:
"""

TEXTURE_META = """fileFormatVersion: 2
guid: {guid}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {{}}
  serializedVersion: 13
  mipmaps:
    mipMapMode: 0
    enableMipMap: 0
    sRGBTexture: 1
    linearTexture: 0
    fadeOut: 0
    borderMipMap: 0
    mipMapsPreserveCoverage: 0
    alphaTestReferenceValue: 0.5
    mipMapFadeDistanceStart: 1
    mipMapFadeDistanceEnd: 3
  bumpmap:
    convertToNormalMap: 0
    externalNormalMap: 0
    heightScale: 0.25
    normalMapFilter: 0
    flipGreenChannel: 0
  isReadable: 0
  streamingMipmaps: 0
  streamingMipmapsPriority: 0
  vTOnly: 0
  ignoreMipmapLimit: 0
  grayScaleToAlpha: 0
  generateCubemap: 6
  cubemapConvolution: 0
  seamlessCubemap: 0
  textureFormat: 1
  maxTextureSize: 2048
  textureSettings:
    serializedVersion: 2
    filterMode: 0
    aniso: 1
    mipBias: 0
    wrapU: 1
    wrapV: 1
    wrapW: 1
  nPOTScale: 0
  lightmap: 0
  compressionQuality: 50
  spriteMode: 1
  spriteExtrude: 1
  spriteMeshType: 1
  alignment: 0
  spritePivot: {{x: 0.5, y: 0.5}}
  spritePixelsToUnits: 16
  spriteBorder: {{x: 0, y: 0, z: 0, w: 0}}
  spriteGenerateFallbackPhysicsShape: 1
  alphaUsage: 1
  alphaIsTransparency: 1
  spriteTessellationDetail: -1
  textureType: 8
  textureShape: 1
  singleChannelComponent: 0
  flipbookRows: 1
  flipbookColumns: 1
  maxTextureSizeSet: 0
  compressionQualitySet: 0
  textureFormatSet: 0
  ignorePngGamma: 0
  applyGammaDecoding: 0
  swizzle: 50462976
  cookieLightType: 0
  platformSettings:
  - serializedVersion: 4
    buildTarget: DefaultTexturePlatform
    maxTextureSize: 2048
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 0
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  spriteSheet:
    serializedVersion: 2
    sprites: []
    outline: []
    customOutline: []
    physicsShape: []
    bones: []
    spriteID: {sprite_id}
    internalID: 0
    vertices: []
    indices:
    edges: []
    weights: []
    secondaryTextures: []
    nameFileIdTable: {{}}
  mipmapLimitGroupName:
  pSDRemoveMatte: 0
  userData:
  assetBundleName:
  assetBundleVariant:
"""


def guid_for(rel_path):
    return hashlib.md5(("clockwise:" + rel_path).encode()).hexdigest()


def write_meta(path, content):
    meta_path = path + ".meta"
    if os.path.exists(meta_path):
        return False
    with open(meta_path, "w", newline="\n") as f:
        f.write(content)
    return True


def main():
    targets = [os.path.join(ROOT, "Assets", "Art"),
               os.path.join(ROOT, "Assets", "Editor")]
    written = 0
    for top in targets:
        rel_top = os.path.relpath(top, ROOT).replace(os.sep, "/")
        written += write_meta(top, FOLDER_META.format(guid=guid_for(rel_top)))
        for dirpath, dirnames, filenames in os.walk(top):
            for name in dirnames:
                p = os.path.join(dirpath, name)
                rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
                written += write_meta(p, FOLDER_META.format(guid=guid_for(rel)))
            for name in filenames:
                if name.endswith(".meta"):
                    continue
                p = os.path.join(dirpath, name)
                rel = os.path.relpath(p, ROOT).replace(os.sep, "/")
                guid = guid_for(rel)
                if name.endswith(".png"):
                    sprite_id = hashlib.md5(
                        ("sprite:" + rel).encode()).hexdigest()
                    written += write_meta(
                        p, TEXTURE_META.format(guid=guid, sprite_id=sprite_id))
                elif name.endswith(".cs"):
                    written += write_meta(p, SCRIPT_META.format(guid=guid))
    print(f"wrote {written} meta files")


if __name__ == "__main__":
    main()
