# After Dark paintings

Gallery panels served directly to the After Dark VRChat world. Each JPEG now contains the artwork and its caption: a larger title, followed by artist and creation year together. All eight filenames and material keys are preserved. Images are at most 2048 pixels on either axis.

The world uses raw.githubusercontent.com URLs and displays its bundled PLEASE ENABLE UNTRUSTED URLS image until a download succeeds. The manifest records dimensions, SHA-256 checksums, artwork and caption rectangles, and physical panel dimensions. Coordinates in pixel rectangles start at the top left.

These files require combined-panel mesh UVs: map the complete front, including the caption, to the same M_Paint_ material. Do not keep a separate visible caption material. The Blender source and Unity reconnect code have been updated for this layout. Existing world builds with old art-only UVs need a subsequent source export and world update; changing these files alone cannot update already-published geometry.
