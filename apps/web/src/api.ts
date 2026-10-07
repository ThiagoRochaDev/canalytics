export async function api<T>(
  path: string,
  options: RequestInit = {},
  workspace = "",
): Promise<T> {
  const res = await fetch("/api" + path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-Canalytics-Request": "1",
      ...(workspace ? { "X-Workspace-ID": workspace } : {}),
      ...options.headers,
    },
  });
  if (!res.ok) {
    let message = "Não foi possível concluir a solicitação.";
    try {
      const d = await res.json();
      message =
        typeof d.detail === "string"
          ? d.detail
          : "Confira os campos preenchidos.";
    } catch {}
    throw new Error(message);
  }
  return res.json();
}
export const post = (body: unknown) => ({
  method: "POST",
  body: JSON.stringify(body),
});
export function saveBlob(blob: Blob, name: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
