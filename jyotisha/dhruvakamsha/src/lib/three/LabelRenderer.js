/**
 * Label rendering for 3D text on the celestial sphere
 */

import * as THREE from 'three';
import { CSS2DRenderer, CSS2DObject } from 'three/examples/jsm/renderers/CSS2DRenderer.js';

/**
 * Create CSS2D renderer for labels
 * @param {HTMLElement} container - Container element
 * @returns {CSS2DRenderer} Label renderer
 */
export function createLabelRenderer(container) {
  const labelRenderer = new CSS2DRenderer();
  labelRenderer.setSize(container.clientWidth, container.clientHeight);
  labelRenderer.domElement.style.position = 'absolute';
  labelRenderer.domElement.style.top = '0';
  labelRenderer.domElement.style.pointerEvents = 'none';
  container.appendChild(labelRenderer.domElement);
  
  return labelRenderer;
}

/**
 * Create a text label at a position
 * @param {string} text - Label text
 * @param {object} position - Position {x, y, z}
 * @param {string} color - CSS color
 * @param {string} className - Optional CSS class
 * @returns {CSS2DObject} Label object
 */
export function createLabel(text, position, color = '#ffffff', className = '') {
  const div = document.createElement('div');
  div.className = `label-3d ${className}`;
  div.textContent = text;
  div.style.color = color;
  div.style.fontSize = '16px';
  div.style.fontWeight = '600';
  div.style.padding = '4px 8px';
  div.style.background = 'rgba(0, 0, 0, 0.7)';
  div.style.borderRadius = '4px';
  div.style.border = `1px solid ${color}`;
  div.style.whiteSpace = 'nowrap';
  div.style.userSelect = 'none';
  div.style.textShadow = '0 0 4px rgba(0,0,0,0.8)';
  
  const label = new CSS2DObject(div);
  label.position.set(position.x, position.y, position.z);
  
  return label;
}

/**
 * Create an arc value label
 * @param {string} value - Arc value text
 * @param {object} position - Position {x, y, z}
 * @param {string} color - CSS color
 * @returns {CSS2DObject} Label object
 */
export function createArcLabel(value, position, color) {
  const div = document.createElement('div');
  div.className = 'arc-label';
  div.textContent = value;
  div.style.color = color;
  div.style.fontSize = '14px';
  div.style.fontWeight = '500';
  div.style.padding = '2px 6px';
  div.style.background = 'rgba(0, 0, 0, 0.8)';
  div.style.borderRadius = '3px';
  div.style.border = `1px solid ${color}`;
  div.style.whiteSpace = 'nowrap';
  div.style.userSelect = 'none';
  
  const label = new CSS2DObject(div);
  label.position.set(position.x, position.y, position.z);
  
  return label;
}

/**
 * Update label renderer size
 * @param {CSS2DRenderer} labelRenderer - Label renderer
 * @param {number} width - New width
 * @param {number} height - New height
 */
export function updateLabelRendererSize(labelRenderer, width, height) {
  labelRenderer.setSize(width, height);
}
