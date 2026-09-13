import { fromMarkdown } from "mdast-util-from-markdown";

// Use source offsets rather than reserialization, preserving nested fences,
// indented code and arbitrary backtick delimiters byte for byte.
function maskCode(body: string) {
  const ranges: [number, number][] = [];
  function visit(node: any) {
    if (node.type === "code" || node.type === "inlineCode") {
      ranges.push([node.position.start.offset, node.position.end.offset]);
      return;
    }
    for (const child of node.children || []) visit(child);
  }
  visit(fromMarkdown(body));
  let prefix = "\u0000wiki-code:";
  while (body.includes(prefix)) prefix += ":";
  const saved = new Map<string, string>();
  let masked = "",
    cursor = 0;
  for (const [start, end] of ranges.sort(([a], [b]) => a - b)) {
    const token = prefix + saved.size + "\u0000";
    saved.set(token, body.slice(start, end));
    masked += body.slice(cursor, start) + token;
    cursor = end;
  }
  return { masked: masked + body.slice(cursor), saved };
}

export function mapMarkdownProse(
  body: string,
  transform: (text: string) => string,
) {
  const { masked, saved } = maskCode(body);
  let result = transform(masked);
  for (const [token, original] of saved)
    result = result.replaceAll(token, () => original);
  return result;
}

export function markdownProse(body: string) {
  return maskCode(body).masked;
}
