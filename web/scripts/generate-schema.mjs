import { mkdir, readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import Ajv2020 from "ajv/dist/2020.js";
import standaloneCode from "ajv/dist/standalone/index.js";

const web = resolve(import.meta.dirname, "..");
const schemaSource = resolve(
  web,
  "../contracts/json-schema/study-workspace/vs01-study-workspace-projection.schema.json",
);
const generated = resolve(web, "src/generated");
const schemaTarget = resolve(generated, "vs01-study-workspace-projection.schema.json");
const typeTarget = resolve(generated, "workspace.ts");
const validatorTarget = resolve(generated, "validate-workspace.js");
const validatorTypesTarget = resolve(generated, "validate-workspace.d.ts");
const schemaBytes = await readFile(schemaSource);
const schema = JSON.parse(schemaBytes.toString("utf8"));
if (!schema.const) throw new Error("workspace schema const is absent");
const typeBytes = Buffer.from(
  `// Generated from the committed VS01 projection schema. Do not edit.\n` +
    `export const VS01_STUDY_WORKSPACE_PROJECTION = ${JSON.stringify(schema.const)} as const;\n` +
    `export type VS01StudyWorkspaceProjection = typeof VS01_STUDY_WORKSPACE_PROJECTION;\n`,
);
const ajv = new Ajv2020({ allErrors: true, strict: true, code: { source: true, esm: true } });
const validatorBytes = Buffer.from(`${standaloneCode(ajv, ajv.compile(schema))}\n`);
const validatorTypes = Buffer.from(
  "declare const validateWorkspace: (value: unknown) => boolean;\nexport default validateWorkspace;\n",
);

if (process.argv.includes("--check")) {
  const [committedSchema, committedType, committedValidator, committedValidatorTypes] = await Promise.all([
    readFile(schemaTarget),
    readFile(typeTarget),
    readFile(validatorTarget),
    readFile(validatorTypesTarget),
  ]);
  if (
    !committedSchema.equals(schemaBytes) ||
    !committedType.equals(typeBytes) ||
    !committedValidator.equals(validatorBytes) ||
    !committedValidatorTypes.equals(validatorTypes)
  )
    process.exitCode = 1;
} else {
  await mkdir(generated, { recursive: true });
  await Promise.all([
    writeFile(schemaTarget, schemaBytes),
    writeFile(typeTarget, typeBytes),
    writeFile(validatorTarget, validatorBytes),
    writeFile(validatorTypesTarget, validatorTypes),
  ]);
}
