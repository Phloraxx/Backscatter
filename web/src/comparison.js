/** Screen-space alignment for visual comparison of two georeferenced radar images.
 * This does not alter scientific inputs or run a water classifier.
 */
export function clampSwipePercent(value) {
  if (!Number.isFinite(value)) return 50;
  return Math.min(95, Math.max(5, value));
}

export function percentFromClientX(clientX, rect) {
  if (!Number.isFinite(clientX) || !rect || rect.width <= 0) return 50;
  return clampSwipePercent(((clientX - rect.left) / rect.width) * 100);
}

/** Map NW/NE/SW corners to an affine CSS image transform.
 * With map pitch disabled, a small local region closely approximates an affine quad.
 */
export function imageAffineCss(projectedCorners, imageWidth, imageHeight) {
  if (!Array.isArray(projectedCorners) || projectedCorners.length !== 4
      || imageWidth <= 0 || imageHeight <= 0) return null;
  const [nw, ne, , sw] = projectedCorners;
  if (![nw?.x,nw?.y,ne?.x,ne?.y,sw?.x,sw?.y].every(Number.isFinite)) return null;
  const a = (ne.x - nw.x) / imageWidth;
  const b = (ne.y - nw.y) / imageWidth;
  const c = (sw.x - nw.x) / imageHeight;
  const d = (sw.y - nw.y) / imageHeight;
  return 'matrix(' + [a,b,c,d,nw.x,nw.y].join(', ') + ')';
}
