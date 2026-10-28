using UnityEditor;
using UnityEngine;

// Forces pixel-art-friendly import settings for every texture under Assets/Art
// so sprites stay crisp (no blur, no compression artifacts) without having to
// configure each file by hand in the Inspector.
public class PixelArtImportSettings : AssetPostprocessor
{
    void OnPreprocessTexture()
    {
        if (!assetPath.StartsWith("Assets/Art"))
            return;

        var importer = (TextureImporter)assetImporter;
        importer.textureType = TextureImporterType.Sprite;
        importer.filterMode = FilterMode.Point;
        importer.textureCompression = TextureImporterCompression.Uncompressed;
        importer.spritePixelsPerUnit = 16f;
        importer.mipmapEnabled = false;
    }
}
