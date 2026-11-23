import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { FBXLoader } from "three/addons/loaders/FBXLoader.js";

const canvas = document.querySelector("[data-body-canvas]");
const stage = document.querySelector("[data-body-stage]");
if (!canvas || !stage) throw new Error("The Body Verse viewer could not be initialized.");

const modelCatalog = JSON.parse(document.querySelector("#body-verse-models").textContent);
const partCatalog = JSON.parse(document.querySelector("#body-verse-catalog").textContent);
const systemCards = [...document.querySelectorAll("[data-system-card]")];
const search = document.querySelector("[data-structure-search]");
const list = document.querySelector("[data-structure-list]");
const listEmpty = document.querySelector("[data-list-empty]");
const listCount = document.querySelector("[data-structure-count]");
const moreButton = document.querySelector("[data-show-more]");
const loading = document.querySelector("[data-body-loading]");
const errorNotice = document.querySelector("[data-body-error]");
const emptyStage = document.querySelector("[data-body-empty]");
const detailName = document.querySelector("[data-detail-name]");
const detailSystem = document.querySelector("[data-detail-system]");
const detailFunction = document.querySelector("[data-detail-function]");
const detailFact = document.querySelector("[data-detail-fact]");
const detailLink = document.querySelector("[data-detail-link]");
const viewerTitle = document.querySelector("[data-viewer-title]");
const viewerSystem = document.querySelector("[data-viewer-system]");
const stageBadge = document.querySelector("[data-stage-badge]");
const stageInstruction = document.querySelector("[data-stage-instruction]");

let renderer;
try {
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
} catch (error) {
  errorNotice.hidden = false;
  errorNotice.textContent = `3D graphics are unavailable in this browser: ${error.message}`;
}
if (!renderer) throw new Error("WebGL is required to show the Body Verse 3D anatomy.");

renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;

const scene = new THREE.Scene();
scene.background = new THREE.Color("#eef2ec");
const camera = new THREE.PerspectiveCamera(36, 1, 0.01, 1000);
camera.position.set(0, 0, 4);
scene.add(new THREE.HemisphereLight("#ffffff", "#829080", 2.3));
const keyLight = new THREE.DirectionalLight("#fff4e8", 3.2);
keyLight.position.set(4, 6, 5);
scene.add(keyLight);
const fillLight = new THREE.DirectionalLight("#d5e5ee", 1.8);
fillLight.position.set(-4, 1, -3);
scene.add(fillLight);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.075;
controls.minDistance = 0.45;
controls.maxDistance = 12;

const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
const loader = new FBXLoader();
const pageSize = 60;
let visibleCount = pageSize;
let structures = [];
let filteredStructures = [];
let activeSystemId = null;
let activeModel = null;
let heartOverlay = null;
let selectedMesh = null;
let requestId = 0;
let pointerStart = null;
let imageMode = false;
let imageScale = 1;
let imagePan = { x: 0, y: 0 };
let imageViewport = null;

const IMAGE_SECTIONS = {
  "whole-body": {
    src: "/static/whole-body.avif",
    hotspots: [
      ["Brain", 50, 8, "Nervous system", "The brain processes information and coordinates thought, movement, and automatic body functions."],
      ["Heart", 50, 31, "Circulatory system", "The heart is a muscular pump that circulates blood through the lungs and the rest of the body."],
      ["Lungs", 50, 27, "Respiratory system", "The lungs exchange oxygen and carbon dioxide between air and blood."],
      ["Liver", 42, 43, "Digestive system", "The liver processes nutrients, makes bile, and helps break down substances in blood."],
      ["Stomach", 58, 43, "Digestive system", "The stomach stores and mixes food with acid and enzymes during digestion."],
      ["Kidneys", 50, 58, "Urinary system", "The kidneys filter blood, balance water and salts, and produce urine."],
      ["Intestines", 50, 68, "Digestive system", "The intestines continue digestion and absorb nutrients and water."],
    ],
  },
  organs: {
    src: "/static/organs.jpg",
    hotspots: [
      ["Brain", 50, 9, "Nervous system", "The brain integrates sensation, thought, movement, and automatic functions."],
      ["Heart", 50, 34, "Circulatory system", "The heart pumps blood through the lungs and the rest of the body."],
      ["Lungs", 50, 29, "Respiratory system", "The lungs exchange oxygen and carbon dioxide."],
      ["Liver", 43, 43, "Digestive system", "The liver processes nutrients and produces bile."],
      ["Stomach", 57, 47, "Digestive system", "The stomach digests food with acid and enzymes."],
      ["Kidneys", 50, 58, "Urinary system", "The kidneys filter blood and form urine."],
      ["Intestines", 50, 68, "Digestive system", "The intestines absorb nutrients and water."],
      ["Bladder", 50, 83, "Urinary system", "The bladder stores urine until it is passed from the body."],
    ],
  },
  nervous: {
    src: "/static/nervous-system.jpg",
    hotspots: [
      ["Brain", 50, 9, "Central nervous system", "The brain integrates information, thought, emotion, sensation, and movement."],
      ["Spinal cord", 50, 38, "Central nervous system", "The spinal cord carries nerve signals between the brain and body."],
      ["Cervical nerves", 42, 23, "Peripheral nervous system", "Cervical nerves help control the head, neck, shoulders, and arms."],
      ["Arm nerves", 22, 49, "Peripheral nervous system", "Peripheral nerves carry signals to and from the arms and hands."],
      ["Leg nerves", 50, 75, "Peripheral nervous system", "Peripheral nerves carry signals to and from the legs and feet."],
    ],
  },
  lymphatic: {
    src: "/static/lymphatic-system.jpg",
    hotspots: [
      ["Lymph nodes", 50, 21, "Lymphatic system", "Clusters of lymph nodes filter lymph and support immune responses."],
      ["Thymus", 50, 31, "Immune system", "The thymus helps T lymphocytes mature."],
      ["Spleen", 58, 49, "Immune system", "The spleen filters blood and helps the immune system respond."],
      ["Pelvic nodes", 50, 66, "Lymphatic system", "Pelvic lymph nodes drain lymph from the lower abdomen and pelvis."],
      ["Leg nodes", 50, 80, "Lymphatic system", "Lower-limb lymph vessels and nodes drain lymph back toward the trunk."],
    ],
  },
};

function resizeViewer() {
  const width = Math.max(stage.clientWidth, 1);
  const height = Math.max(stage.clientHeight, 1);
  renderer.setSize(width, height, false);
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
}

function applyImageTransform() {
  if (!imageViewport) return;
  const frame = imageViewport.querySelector(".anatomy-image-frame");
  if (frame) {
    frame.style.transform = `translate(${imagePan.x}px, ${imagePan.y}px) scale(${imageScale})`;
  }
}

function setImageDetails(name, system, summary) {
  detailName.textContent = name;
  detailSystem.textContent = system;
  detailFunction.textContent = summary;
  detailFact.textContent = "Use the zoom controls or scroll to inspect this anatomical region more closely.";
  for (const hotspot of imageViewport?.querySelectorAll(".anatomy-hotspot") || []) {
    hotspot.classList.toggle("selected", hotspot.dataset.name === name);
  }
  for (const row of list.querySelectorAll(".body-part-button")) {
    row.classList.toggle("selected", row.dataset.structureName === name);
    row.setAttribute("aria-pressed", String(row.dataset.structureName === name));
  }
}

function loadImageSection(systemId) {
  const section = IMAGE_SECTIONS[systemId];
  if (!section) return false;
  imageMode = true;
  stage.classList.add("image-anatomy");
  canvas.style.display = "none";
  controls.enabled = false;
  emptyStage.hidden = true;
  loading.hidden = true;
  errorNotice.hidden = true;
  search.disabled = false;
  search.placeholder = "Search structure";
  search.value = "";
  if (imageViewport) imageViewport.remove();
  imageScale = 1;
  imagePan = { x: 0, y: 0 };

  imageViewport = document.createElement("div");
  imageViewport.className = "anatomy-image-viewport";
  const image = document.createElement("img");
  image.src = section.src;
  image.alt = modelCatalog[systemId].label + " anatomical illustration";
  image.draggable = false;
  const imageFrame = document.createElement("div");
  imageFrame.className = "anatomy-image-frame";
  imageFrame.append(image);
  imageViewport.append(imageFrame);

  for (const [name, x, y, system, summary] of section.hotspots) {
    const hotspot = document.createElement("button");
    hotspot.type = "button";
    hotspot.className = "anatomy-hotspot";
    hotspot.dataset.name = name;
    hotspot.style.left = `${x}%`;
    hotspot.style.top = `${y}%`;
    hotspot.setAttribute("aria-label", `Select ${name}`);
    hotspot.innerHTML = '<span></span>';
    hotspot.addEventListener("click", (event) => {
      event.stopPropagation();
      setImageDetails(name, system, summary);
    });
    imageFrame.append(hotspot);
  }

  stage.append(imageViewport);
  applyImageTransform();
  imageViewport.addEventListener("wheel", (event) => {
    event.preventDefault();
    imageScale = Math.max(1, Math.min(3.5, imageScale + (event.deltaY < 0 ? 0.12 : -0.12)));
    applyImageTransform();
  }, { passive: false });

  let dragStart = null;
  imageViewport.addEventListener("pointerdown", (event) => {
    if (event.target.closest(".anatomy-hotspot")) return;
    dragStart = { x: event.clientX, y: event.clientY, panX: imagePan.x, panY: imagePan.y };
    imageViewport.setPointerCapture(event.pointerId);
  });
  imageViewport.addEventListener("pointermove", (event) => {
    if (!dragStart) return;
    imagePan.x = dragStart.panX + event.clientX - dragStart.x;
    imagePan.y = dragStart.panY + event.clientY - dragStart.y;
    applyImageTransform();
  });
  imageViewport.addEventListener("pointerup", () => { dragStart = null; });
  imageViewport.addEventListener("pointercancel", () => { dragStart = null; });

  structures = section.hotspots.map(([, , , system, summary], index) =>
    ({ name: section.hotspots[index][0], system, summary }),
  );
  listCount.textContent = String(structures.length);
  list.replaceChildren();
  for (const item of structures) {
    const row = document.createElement("button");
    row.type = "button";
    row.className = "body-part-button";
    row.dataset.structureName = item.name;
    row.setAttribute("aria-pressed", "false");
    const label = document.createElement("span");
    label.textContent = item.name;
    row.append(label);
    row.addEventListener("click", () => setImageDetails(item.name, item.system, item.summary));
    list.append(row);
  }
  listEmpty.hidden = true;
  moreButton.hidden = true;
  viewerSystem.textContent = "ANATOMICAL ILLUSTRATION";
  viewerTitle.textContent = modelCatalog[systemId].label;
  if (stageBadge) stageBadge.textContent = "Anatomical illustration";
  if (stageInstruction) stageInstruction.innerHTML = "Drag to pan<small>Click a structure to see its details</small>";
  detailName.textContent = modelCatalog[systemId].label;
  detailSystem.textContent = "ANATOMY EXPLORER";
  detailFunction.textContent = modelCatalog[systemId].description;
  detailFact.textContent = "Choose a highlighted region or a structure from the list to see its details.";
  return true;
}

function normalizedName(name) {
  return name
    .toLowerCase()
    .replace(/[._()[\]]/g, " ")
    .replace(/\s+/g, " ")
    .replace(/\s+[lr]$/, "")
    .trim();
}

function getStructureDetails(displayName, systemName) {
  const name = displayName.replace(/[._]+/g, " ").replace(/\s+/g, " ").trim();
  const normalized = normalizedName(name);
  const curated = Object.entries(partCatalog).find(([key]) =>
    normalized.includes(key) || key.includes(normalized),
  )?.[1];
  if (curated) {
    return {
      name: curated.name,
      system: curated.system,
      summary: curated.summary,
      fact: curated.fact,
      link: `https://medlineplus.gov/search/?query=${encodeURIComponent(curated.name)}`,
    };
  }
  let summary;
  let link;
  if (/(brain|cerebr|medulla|spinal|nerve|neuron|optic|cochlea)/.test(normalized)) {
    summary = `${name} is part of the nervous system. Nervous structures transmit, process, or coordinate signals that support sensation, movement, and automatic body functions.`;
    link = `https://www.ncbi.nlm.nih.gov/books/NBK537116/?term=${encodeURIComponent(name)}`;
  } else if (/(arter|vein|aorta|vena|vessel|pulmonary)/.test(normalized)) {
    summary = `${name} is a blood-vessel structure of the circulatory system. It helps carry blood between the heart and tissues, or between the heart and lungs.`;
    link = `https://medlineplus.gov/bloodvessels.html`;
  } else if (/(muscle|tendon|deltoid|biceps|pector|quadriceps|abdom|calf)/.test(normalized)) {
    summary = `${name} is a muscle or muscle-related structure. It contributes to movement, posture, stability, or force transfer through the musculoskeletal system.`;
    link = `https://medlineplus.gov/muscles.html`;
  } else if (/(bone|skull|rib|vertebra|spine|pelvis|humerus|femur|joint|cartilage)/.test(normalized)) {
    summary = `${name} is a bone or joint structure in the musculoskeletal system. It helps support the body, protect organs, enable movement, or transfer load.`;
    link = `https://medlineplus.gov/bones.html`;
  } else if (/(lung|liver|kidney|stomach|pancreas|spleen|colon|intestin|bladder|gall|thymus|heart|digest|respir|urinar|lymph)/.test(normalized)) {
    summary = `${name} is an anatomical organ or organ-related structure. It contributes to organ-system functions such as breathing, circulation, digestion, filtration, immunity, or storage.`;
    link = `https://medlineplus.gov/search/?query=${encodeURIComponent(name)}`;
  } else {
    summary = `${name} is a named anatomical structure in this 3D atlas. It can be identified in relation to neighbouring tissues and viewed from different angles for study.`;
    link = `https://en.wikipedia.org/wiki/${encodeURIComponent(name.replaceAll(" ", "_"))}`;
  }
  return {
    name,
    system: systemName || "Anatomical structure",
    summary,
    fact: "Structure names and relations can vary by anatomical atlas; use the reference link to confirm terminology.",
    link,
  };
}

function setDetails(mesh) {
  selectedMesh = mesh;
  const displayName = mesh.name.replace(/[._]+/g, " ").replace(/\s+/g, " ").trim();
  const details = getStructureDetails(
    displayName,
    modelCatalog[activeSystemId]?.label,
  );
  detailName.textContent = details.name;
  detailSystem.textContent = details.system;
  detailFunction.textContent = details.summary;
  detailFact.textContent = details.fact;
  if (detailLink) {
    detailLink.href = details.link;
    detailLink.hidden = false;
  }
  for (const row of list.querySelectorAll(".body-part-button")) {
    const active = row.dataset.structureIndex === String(structures.indexOf(mesh));
    row.classList.toggle("selected", active);
    row.setAttribute("aria-pressed", String(active));
  }
  for (const item of structures) {
    const materials = item.userData.bodyVerseMaterials || [];
    for (const material of materials) {
      material.emissive?.set(item === mesh ? "#c4744d" : "#000000");
      if (material.emissive) material.emissiveIntensity = item === mesh ? 0.4 : 0;
    }
  }
}

function renderList() {
  const query = normalizedName(search.value);
  filteredStructures = structures.filter((mesh) =>
    normalizedName(mesh.name || "Structure").includes(query),
  );
  listCount.textContent = filteredStructures.length.toLocaleString();
  list.replaceChildren();
  const items = filteredStructures.slice(0, visibleCount);
  for (const mesh of items) {
    const row = document.createElement("button");
    const index = structures.indexOf(mesh);
    row.type = "button";
    row.className = "body-part-button";
    row.dataset.structureIndex = String(index);
    row.setAttribute("aria-pressed", String(mesh === selectedMesh));
    const label = document.createElement("span");
    label.textContent = (mesh.name || `Structure ${index + 1}`).replace(/[._]+/g, " ").trim();
    row.append(label);
    row.addEventListener("click", () => setDetails(mesh));
    list.append(row);
  }
  listEmpty.hidden = structures.length > 0;
  listEmpty.textContent = activeSystemId
    ? "No structures match this search."
    : "Choose a system to load its structure list.";
  moreButton.hidden = filteredStructures.length <= visibleCount;
}

function disposeModel(model) {
  model.traverse((object) => {
    if (!object.isMesh) return;
    object.geometry?.dispose();
    for (const material of object.userData.bodyVerseMaterials || []) material.dispose();
  });
  scene.remove(model);
  if (heartOverlay) {
    scene.remove(heartOverlay);
    heartOverlay = null;
  }
}

function createHeartOverlay() {
  if (heartOverlay) {
    scene.remove(heartOverlay);
    heartOverlay = null;
  }
  const group = new THREE.Group();
  group.name = "Whole body heart overlay";
  const material = new THREE.MeshPhysicalMaterial({
    color: "#df4f63",
    roughness: 0.42,
    metalness: 0.02,
    clearcoat: 0.35,
    clearcoatRoughness: 0.32,
  });
  const leftLobe = new THREE.Mesh(new THREE.IcosahedronGeometry(0.20, 4), material);
  leftLobe.name = "Heart";
  leftLobe.position.set(-0.10, 0.38, 0.48);
  leftLobe.scale.set(0.88, 1.08, 0.68);
  const rightLobe = new THREE.Mesh(new THREE.IcosahedronGeometry(0.16, 4), material);
  rightLobe.name = "Heart";
  rightLobe.position.set(0.10, 0.40, 0.50);
  rightLobe.scale.set(0.86, 1.18, 0.66);
  const lowerLobe = new THREE.Mesh(new THREE.IcosahedronGeometry(0.16, 4), material);
  lowerLobe.name = "Heart";
  lowerLobe.position.set(-0.03, 0.20, 0.49);
  lowerLobe.scale.set(0.92, 1.22, 0.66);
  for (const mesh of [leftLobe, rightLobe, lowerLobe]) {
    mesh.userData.bodyVerseMaterials = [material];
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    group.add(mesh);
  }
  heartOverlay = group;
  scene.add(group);
  return [leftLobe, rightLobe, lowerLobe];
}

function fitModel(model) {
  const bounds = new THREE.Box3().setFromObject(model);
  const size = bounds.getSize(new THREE.Vector3());
  const center = bounds.getCenter(new THREE.Vector3());
  const longestSide = Math.max(size.x, size.y, size.z);
  const targetHeight = model.name === "Whole body" ? 2.35 : 2.8;
  const scale = targetHeight / (longestSide || 1);
  model.scale.setScalar(scale);
  model.position.copy(center).multiplyScalar(-scale);
  model.updateMatrixWorld(true);
  controls.target.set(0, 0, 0);
  camera.position.set(0, 0, 4.2);
  controls.minDistance = 0.35;
  controls.maxDistance = 10;
  controls.update();
}

function finishLoading(model, systemId, thisRequest) {
  if (thisRequest !== requestId) {
    disposeModel(model);
    return;
  }
  activeModel = model;
  structures = [];
  model.traverse((object) => {
    if (!object.isMesh || !object.geometry?.attributes?.position) return;
    object.userData.bodyVerseMaterials = (Array.isArray(object.material)
      ? object.material
      : [object.material]).map((material) => material.clone());
    object.material = Array.isArray(object.material)
      ? object.userData.bodyVerseMaterials
      : object.userData.bodyVerseMaterials[0];
    const name = normalizedName(object.name);
    const palette = name.includes("heart") || name.includes("aorta")
      ? "#df4f63"
      : name.includes("lung") || name.includes("bronch")
        ? "#67aeb2"
        : name.includes("liver")
          ? "#a87350"
          : name.includes("kidney")
            ? "#7e6ac1"
            : name.includes("stomach")
              ? "#dda167"
              : name.includes("brain") || name.includes("cerebr")
                ? "#b58ad7"
                : name.includes("bone") || name.includes("rib") || name.includes("skull") || name.includes("vertebra")
                  ? "#d7ca9a"
                  : name.includes("muscle")
                    ? "#c96e73"
                    : name.includes("vein") || name.includes("vena")
                      ? "#4d74ad"
                      : name.includes("arter")
                        ? "#d45a67"
                        : null;
    if (palette) {
      for (const material of object.userData.bodyVerseMaterials) {
        material.color?.set(palette);
        material.roughness = 0.48;
        material.metalness = 0.03;
        if (material.emissive) material.emissive.set(palette).multiplyScalar(0.08);
      }
    }
    object.castShadow = true;
    object.receiveShadow = true;
    structures.push(object);
  });
  fitModel(model);
  scene.add(model);
  activeSystemId = systemId;
  selectedMesh = null;
  structures.sort((left, right) => left.name.localeCompare(right.name));
  visibleCount = pageSize;
  search.disabled = false;
  search.placeholder = "Search structures";
  viewerSystem.textContent = "LICENSED 3D ANATOMY";
  viewerTitle.textContent = modelCatalog[systemId].label;
  if (stageBadge) stageBadge.textContent = "Licensed 3D anatomy";
  if (stageInstruction) stageInstruction.innerHTML = "Drag to rotate<small>Click a structure to see its details</small>";
  emptyStage.hidden = true;
  loading.hidden = true;
  errorNotice.hidden = true;
  listEmpty.hidden = structures.length !== 0;
  listEmpty.textContent = structures.length
    ? ""
    : "No named structures were found in this model.";
  renderList();
}

function loadSketchfabSection(systemId) {
  const system = modelCatalog[systemId];
  if (!system?.embed) return false;
  activeSystemId = systemId;
  activeModel = null;
  structures = [];
  canvas.style.display = "none";
  controls.enabled = false;
  emptyStage.hidden = true;
  loading.hidden = true;
  errorNotice.hidden = true;
  if (imageViewport) imageViewport.remove();
  imageViewport = null;

  const wrapper = document.createElement("div");
  wrapper.className = "sketchfab-anatomy";
  const iframe = document.createElement("iframe");
  iframe.title = system.label;
  iframe.allow = "autoplay; fullscreen; xr-spatial-tracking";
  iframe.src = `https://sketchfab.com/models/${system.embed}/embed?autostart=1&ui_theme=light&transparent=1&ui_infos=0&ui_watermark=0&ui_controls=0&ui_stop=0&ui_help=0&ui_settings=0&ui_vr=0&ui_fullscreen=0&ui_annotations=0&annotations_visible=0&dnt=1`;
  wrapper.append(iframe);
  stage.append(wrapper);
  imageViewport = wrapper;

  if (window.Sketchfab) {
    const client = new window.Sketchfab(iframe);
    client.init(system.embed, {
      success: (api) => {
        api.start();
        api.addEventListener("annotationSelect", (annotationIndex) => {
          api.getAnnotation(annotationIndex, (annotationError, annotation) => {
            if (annotationError || !annotation?.name) return;
            const details = getStructureDetails(annotation.name, system.label);
            detailName.textContent = details.name;
            detailSystem.textContent = details.system;
            detailFunction.textContent = details.summary;
            detailFact.textContent = details.fact;
            if (detailLink) {
              detailLink.href = details.link;
              detailLink.hidden = false;
            }
          });
        });
      },
      error: () => {
        viewerSystem.textContent = "MODEL UNAVAILABLE";
        detailFact.textContent = "This Sketchfab model could not be displayed. Use the structure list or try again with internet access.";
      },
    });
  }

  const structurePresets = {
    organs: [
      ["Heart", "Circulatory system"],
      ["Lungs", "Respiratory system"],
      ["Liver", "Digestive system"],
      ["Stomach", "Digestive system"],
      ["Pancreas", "Digestive system"],
      ["Spleen", "Immune system"],
      ["Kidneys", "Urinary system"],
      ["Small intestine", "Digestive system"],
      ["Large intestine", "Digestive system"],
      ["Bladder", "Urinary system"],
    ],
    nervous: [
      ["Brain", "Central nervous system"],
      ["Spinal cord", "Central nervous system"],
      ["Cervical nerves", "Peripheral nervous system"],
      ["Arm nerves", "Peripheral nervous system"],
      ["Thoracic nerves", "Peripheral nervous system"],
      ["Lumbar nerves", "Peripheral nervous system"],
      ["Sacral nerves", "Peripheral nervous system"],
      ["Sciatic nerve", "Peripheral nervous system"],
    ],
    lymphatic: [
      ["Lymph nodes", "Lymphatic system"],
      ["Lymph vessels", "Lymphatic system"],
      ["Thymus", "Immune system"],
      ["Spleen", "Immune system"],
      ["Thoracic duct", "Lymphatic system"],
      ["Peyer patches", "Immune system"],
      ["Tonsils", "Immune system"],
    ],
  };
  structures = (structurePresets[systemId] || []).map(([name, systemName]) => ({
    name,
    systemName,
  }));
  list.replaceChildren();
  listCount.textContent = String(structures.length);
  for (const item of structures) {
    const row = document.createElement("button");
    row.type = "button";
    row.className = "body-part-button";
    row.dataset.structureName = item.name;
    row.innerHTML = `<span>${item.name}</span>`;
    row.addEventListener("click", () => {
      const details = getStructureDetails(item.name, item.systemName);
      detailName.textContent = details.name;
      detailSystem.textContent = details.system;
      detailFunction.textContent = details.summary;
      detailFact.textContent = details.fact;
      if (detailLink) {
        detailLink.href = details.link;
        detailLink.hidden = false;
      }
    });
    list.append(row);
  }
  listEmpty.hidden = true;
  moreButton.hidden = true;
  search.disabled = false;
  search.placeholder = "Search structure";
  search.value = "";
  viewerSystem.textContent = "INTERACTIVE 3D MODEL";
  viewerTitle.textContent = system.label;
  detailName.textContent = system.label;
  detailSystem.textContent = "ANATOMY EXPLORER";
  detailFunction.textContent = system.description;
  detailFact.textContent = "Use the model controls to rotate and zoom. Select a listed structure or an available model region to view details.";
  if (detailLink) detailLink.hidden = true;
  if (stageBadge) stageBadge.textContent = "Interactive Sketchfab 3D";
  if (stageInstruction) stageInstruction.innerHTML = "Drag to rotate<small>Scroll or pinch to zoom</small>";

  return true;
}

function loadSystem(systemId) {
  const system = modelCatalog[systemId];
  if (!system) return;
  const thisRequest = ++requestId;
  if (activeModel) disposeModel(activeModel);
  if (imageViewport) imageViewport.remove();
  imageViewport = null;
  imageMode = false;
  stage.classList.remove("image-anatomy");
  canvas.style.display = "";
  controls.enabled = true;
  activeModel = null;
  activeSystemId = systemId;
  structures = [];
  selectedMesh = null;
  search.value = "";
  search.disabled = true;
  list.replaceChildren();
  listCount.textContent = "0";
  listEmpty.hidden = false;
  listEmpty.textContent = "Loading anatomical structures…";
  emptyStage.hidden = true;
  errorNotice.hidden = true;
  loading.hidden = false;
  viewerTitle.textContent = system.label;
  viewerSystem.textContent = "LOADING 3D MODEL";
  detailName.textContent = system.label;
  detailSystem.textContent = "ANATOMY EXPLORER";
  detailFunction.textContent = system.description;
  detailFact.textContent = `The ${system.size} 3D model downloads from its openly licensed source when selected.`;
  for (const card of systemCards) {
    const selected = card.dataset.systemCard === systemId;
    card.classList.toggle("active", selected);
    card.setAttribute("aria-pressed", String(selected));
  }

  if (loadSketchfabSection(systemId)) return;

  loader.load(
    system.model,
    (model) => finishLoading(model, systemId, thisRequest),
    (event) => {
      if (thisRequest !== requestId) return;
      const progress = event.total
        ? `${Math.round((event.loaded / event.total) * 100)}%`
        : `${(event.loaded / (1024 * 1024)).toFixed(1)} MB loaded`;
      document.querySelector("[data-loading-progress]").textContent = progress;
    },
    (error) => {
      if (thisRequest !== requestId) return;
      loading.hidden = true;
      errorNotice.hidden = false;
      errorNotice.textContent = `The 3D model could not be loaded. Check your internet connection and try this system again. ${error?.message || ""}`;
      viewerSystem.textContent = "MODEL UNAVAILABLE";
      listEmpty.hidden = false;
      listEmpty.textContent = "The model did not load.";
    },
  );
}

for (const card of systemCards) {
  card.addEventListener("click", () => loadSystem(card.dataset.systemCard));
}
search.addEventListener("input", () => {
  visibleCount = pageSize;
  if (imageMode) {
    const query = normalizedName(search.value);
    for (const row of list.querySelectorAll(".body-part-button")) {
      row.hidden = query && !normalizedName(row.dataset.structureName).includes(query);
    }
    return;
  }
  renderList();
});
moreButton.addEventListener("click", () => {
  visibleCount += pageSize;
  renderList();
});

for (const button of document.querySelectorAll("[data-camera]")) {
  button.addEventListener("click", () => {
    if (imageMode) {
      if (button.dataset.camera === "reset") {
        imageScale = 1;
        imagePan = { x: 0, y: 0 };
      } else {
        imageScale = Math.max(1, Math.min(3.5,
          imageScale + (button.dataset.camera === "zoom-in" ? 0.25 : -0.25),
        ));
      }
      applyImageTransform();
      return;
    }
    if (button.dataset.camera === "reset" && activeModel) {
      fitModel(activeModel);
      return;
    }
    const factor = button.dataset.camera === "zoom-in" ? 0.8 : 1.25;
    camera.position.copy(controls.target).add(
      camera.position.clone().sub(controls.target).multiplyScalar(factor),
    );
    controls.update();
  });
}

canvas.addEventListener("pointerdown", (event) => {
  pointerStart = { x: event.clientX, y: event.clientY };
});
canvas.addEventListener("pointerup", (event) => {
  if (!pointerStart || !activeModel) return;
  const moved = Math.hypot(event.clientX - pointerStart.x, event.clientY - pointerStart.y);
  pointerStart = null;
  if (moved > 5) return;
  const bounds = canvas.getBoundingClientRect();
  pointer.set(
    ((event.clientX - bounds.left) / bounds.width) * 2 - 1,
    -((event.clientY - bounds.top) / bounds.height) * 2 + 1,
  );
  raycaster.setFromCamera(pointer, camera);
  const hit = raycaster.intersectObjects(structures, false)[0];
  if (hit) setDetails(hit.object);
});
canvas.addEventListener("pointercancel", () => { pointerStart = null; });

new ResizeObserver(resizeViewer).observe(stage);
resizeViewer();
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();
loadSystem("whole-body");
