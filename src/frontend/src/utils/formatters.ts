export function sanitizeTitle(title: string): string {
  // Remove any special characters except letters, numbers, spaces, and common punctuation
  return title.replace(/[^\w\s.-]/g, "").trim();
}
