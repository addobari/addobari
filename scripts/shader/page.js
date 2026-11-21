import { ShaderMount, meshGradientFragmentShader, flutedGlassFragmentShader, getShaderColorFromString,
  ShaderFitOptions, GlassGridShapes, GlassDistortionShapes, defaultObjectSizing } from "@paper-design/shaders";

const sizing = (o) => { const s = { ...defaultObjectSizing, ...o }; return {
  u_fit: ShaderFitOptions[s.fit], u_rotation: s.rotation, u_scale: s.scale, u_offsetX: s.offsetX, u_offsetY: s.offsetY,
  u_originX: s.originX, u_originY: s.originY, u_worldWidth: s.worldWidth, u_worldHeight: s.worldHeight }; };

window.setup = (cfg) => {
  const meshEl = document.getElementById("mesh"), glassEl = document.getElementById("glass");
  for (const el of [meshEl, glassEl]) { el.style.width = cfg.w + "px"; el.style.height = cfg.h + "px"; }
  const attrs = { preserveDrawingBuffer: true, premultipliedAlpha: false };
  window.mesh = new ShaderMount(meshEl, meshGradientFragmentShader, {
    u_colors: cfg.colors.map(getShaderColorFromString), u_colorsCount: cfg.colors.length,
    u_distortion: 0.85, u_swirl: 0.35, u_grainMixer: 0.25, u_grainOverlay: cfg.grain, ...sizing({ fit: "cover" }),
  }, attrs, 0, 0, cfg.ratio, 1e8);
  window.glass = new ShaderMount(glassEl, flutedGlassFragmentShader, {
    u_image: undefined, u_imageAspectRatio: cfg.w / cfg.h,
    u_colorBack: getShaderColorFromString("#00000000"), u_colorShadow: getShaderColorFromString("#000000"),
    u_colorHighlight: getShaderColorFromString("#ffffff"), u_shadows: 0.25, u_highlights: 0.1,
    u_size: 0.82, u_angle: 0, u_distortion: 0.5, u_shift: 0.3, u_blur: 0.2, u_edges: 0.0, u_stretch: 0,
    u_marginLeft: 0, u_marginRight: 0, u_marginTop: 0, u_marginBottom: 0, u_grainMixer: 0, u_grainOverlay: 0,
    u_shape: GlassGridShapes.lines, u_distortionShape: GlassDistortionShapes.prism, ...sizing({ fit: "cover" }),
  }, attrs, 0, 0, cfg.ratio, 1e8);
  return true;
};

window.renderFrame = async (ms) => {
  mesh.setFrame(ms);
  const src = mesh.canvasElement.toDataURL("image/png");
  const img = new Image(); img.src = src; await img.decode();
  glass.setUniforms({ u_image: img });
  glass.setFrame(0);
  return glass.canvasElement.toDataURL("image/png");
};
