// Node counts empty test files as successful synthetic tests. Retain individual
// events so release qualification can require real assertions in every file.
export default async function* reportTests(events) {
  for await (const { type, data } of events) {
    if (type !== "test:pass" && type !== "test:fail") continue;
    yield JSON.stringify({
      event: type,
      name: data.name,
      file: data.file,
      type: data.details?.type,
      skip: Boolean(data.skip),
      todo: Boolean(data.todo),
    }) + "\n";
  }
}
