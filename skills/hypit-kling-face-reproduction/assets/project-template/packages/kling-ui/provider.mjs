import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile, rename, stat, realpath } from 'node:fs/promises';
import { resolve, relative, sep, isAbsolute, join } from 'node:path';
import { defineEndpointPackage, wakeAfter } from '@hypit/hypit/endpoint-kit';
import { artifactTypes } from '@hypit/hypit/artifact';
import { capability, moduleRef, identityPorts } from './author.mjs';

const hash = bytes => createHash('sha256').update(bytes).digest('hex');
function videoExtension(artifact) {
  if (artifact.mediaType === 'video/mp4') return '.mp4';
  if (artifact.mediaType === 'video/quicktime') return '.mov';
  throw new Error('Use an actual MP4/MOV input container; renaming a file is not conversion');
}
function inside(root, file) {
  const target = resolve(root, file), rel = relative(root, target);
  if (rel === '..' || rel.startsWith(`..${sep}`) || isAbsolute(rel)) throw new Error('Result path must stay inside its exchange job');
  return target;
}
async function readJson(path) {
  try { return JSON.parse(await readFile(path, 'utf8')); }
  catch (error) { if (error.code === 'ENOENT') return undefined; throw error; }
}
async function writeJson(path, value) {
  const temporary = `${path}.${process.pid}.tmp`;
  await writeFile(temporary, JSON.stringify(value, null, 2) + '\n', { flag: 'w' });
  await rename(temporary, path);
}
async function stageInput(path, bytes) {
  try { await writeFile(path, bytes, { flag: 'wx' }); }
  catch (error) {
    if (error.code !== 'EEXIST') throw error;
    if (hash(await readFile(path)) !== hash(bytes)) throw new Error('Existing staged input differs from this frozen request');
  }
}
async function containedResult(directory, file) {
  const path = inside(directory, file);
  const physicalRoot = await realpath(directory), physicalPath = await realpath(path);
  inside(physicalRoot, physicalPath);
  return physicalPath;
}
// Hypit's OperationReceipt is exactly { id: string, url?: string }. This ID names
// the local human-service request; actual Kling evidence stays in receipt.json.
const publicReceipt = (jobId) => ({ id: `kling-ui-local:${jobId}` });

export function createKlingUiProvider({ instance, pool, exchangeRoot, pollIntervalMs = 5000 }) {
  const root = resolve(exchangeRoot);
  const jobFrom = context => {
    const jobId = context.handle?.jobId;
    if (typeof jobId !== 'string' || !/^[a-f0-9]{24}$/.test(jobId)) throw new Error('Invalid local request handle');
    return { jobId, directory: inside(root, jobId) };
  };
  const endpoint = {
    async start(context) {
      const authored = context.need.constraints;
      if (authored.source?.kind !== 'blob' || !authored.source.mediaType.startsWith('video/') || typeof authored.prompt !== 'string') throw new Error('Incomplete Kling UI request');
      if (authored.sourceUpload?.kind !== 'blob' || !authored.sourceUpload.mediaType.startsWith('video/')) throw new Error('Missing compatible upload video artifact');
      if (authored.sourcePersonReference !== true || authored.uploadVideoPersonReference !== true) throw new Error('Both original and compatible video must be declared as containing people');
      if (!Array.isArray(authored.identities) || authored.identities.length !== 5
        || authored.identities.some((item, index) => item.port !== identityPorts[index] || item.personReference !== true
          || item.artifact?.kind !== 'blob' || !item.artifact.mediaType.startsWith('image/'))) {
        throw new Error('Exactly five independent portrait ports, in front/left45/right45/left90/right90 order, are required');
      }
      const jobId = hash(Buffer.from(context.operation)).slice(0, 24);
      const directory = inside(root, jobId);
      await mkdir(directory, { recursive: true });
      const existing = await readJson(join(directory, 'request.json'));
      if (!existing) {
        const source = await context.resources.get(authored.source.resource);
        if (!source) throw new Error('Missing original video artifact bytes');
        const sourceFile = 'source' + videoExtension(authored.source);
        await stageInput(join(directory, sourceFile), source);
        const uploadVideo = await context.resources.get(authored.sourceUpload.resource);
        if (!uploadVideo || uploadVideo.length !== authored.sourceUpload.size) throw new Error('Missing or changed compatible upload video');
        const uploadFile = 'upload-video' + videoExtension(authored.sourceUpload);
        await stageInput(join(directory, uploadFile), uploadVideo);
        const identities = [];
        for (const item of authored.identities) {
          const bytes = await context.resources.get(item.artifact.resource);
          if (!bytes || bytes.length !== item.artifact.size) throw new Error(`Missing or changed portrait bytes for ${item.port}`);
          const extension = item.artifact.mediaType === 'image/png' ? 'png' : item.artifact.mediaType === 'image/webp' ? 'webp' : 'jpg';
          const file = `identity-${item.port}.${extension}`;
          await stageInput(join(directory, file), bytes);
          identities.push({ port: item.port, file, resource: item.artifact.resource, sha256: hash(bytes), size: bytes.length,
            mediaType: item.artifact.mediaType, personReference: true, referenceOrder: identities.length + 1 });
        }
        await writeJson(join(directory, 'request.json'), {
          format: 'hypit.kling-ui-five-view-request@1', jobId, createdAt: new Date().toISOString(),
          service: 'Kling browser UI', state: 'awaiting-ui', prompt: authored.prompt,
          inputs: {
            source: { file: sourceFile, resource: authored.source.resource, sha256: hash(source), size: source.length, personReference: true, role: 'original-timing-audio-reference' },
            uploadVideo: { file: uploadFile, resource: authored.sourceUpload.resource, sha256: hash(uploadVideo), size: uploadVideo.length, personReference: true, role: 'compatible-copy-for-upload-as-Video1' },
            identities,
          },
          submission: { authorized: false, state: 'not-submitted', reason: '本次付费尚未批准；本地Build只准备请求并等待页面操作。' },
          resultContract: { file: 'result.mp4', receipt: 'receipt.json', requiredReceiptFields: ['jobId', 'status', 'model', 'output', 'sha256'], audioPolicy: 'restore-original-after-download' },
        });
      }
      const handle = { jobId }, receipt = publicReceipt(jobId);
      await context.checkpoint?.({ handle, receipt });
      return { ...wakeAfter(handle, pollIntervalMs, Date.now(), { phase: '等待可灵页面操作，尚未确认付费提交' }), receipt };
    },
    async poll(context) {
      const { jobId, directory } = jobFrom(context);
      const receipt = await readJson(join(directory, 'receipt.json'));
      if (!receipt) return wakeAfter({ jobId }, pollIntervalMs, Date.now(), { phase: '等待可灵页面操作，尚未确认付费提交' });
      if (receipt.jobId !== jobId) throw new Error('Receipt belongs to another request');
      if (['submitted', 'running'].includes(receipt.status)) return { ...wakeAfter({ jobId }, pollIntervalMs, Date.now(), { phase: receipt.status === 'submitted' ? '可灵已提交' : '可灵生成中' }), receipt: publicReceipt(jobId, receipt) };
      if (receipt.status === 'failed') return { status: 'failed', receipt: publicReceipt(jobId, receipt), failure: { code: 'KLING_UI_FAILED', message: String(receipt.message || 'Kling UI generation failed') } };
      if (receipt.status !== 'succeeded') throw new Error('Unknown Kling UI receipt status');
      if (typeof receipt.model !== 'string' || !receipt.model.trim() || typeof receipt.output !== 'string' || !/^[a-f0-9]{64}$/.test(receipt.sha256 ?? '')) throw new Error('Completion receipt needs actual model label, output path and SHA256');
      const path = await containedResult(directory, receipt.output);
      if (!(await stat(path)).isFile()) throw new Error('Result is not a local file');
      return { status: 'ready', handle: { jobId, output: receipt.output, sha256: receipt.sha256 }, receipt: publicReceipt(jobId, receipt) };
    },
    async collect(context) {
      const { jobId, directory } = jobFrom(context);
      const bytes = await readFile(await containedResult(directory, context.handle.output));
      if (hash(bytes) !== context.handle.sha256) throw new Error('Downloaded result SHA256 changed');
      if (bytes.length < 16 || bytes.toString('ascii', 4, 8) !== 'ftyp') throw new Error('Result must be an MP4 file');
      await context.reportProgress?.({ phase: '将可灵下载视频写入 Hypit Result' });
      const artifact = await context.resources.put(bytes, 'video/mp4');
      return { status: 'completed', result: { value: artifact }, receipt: publicReceipt(jobId, await readJson(join(directory, 'receipt.json'))) };
    },
    async cancel() { return { status: 'unsupported' }; },
  };
  return defineEndpointPackage({ module: moduleRef, facet: 'kling-ui', instance, pool, credentials: {}, defaultConcurrency: 1,
    actionLimits: { submit: { concurrency: 1 }, poll: { concurrency: 1 }, collect: { concurrency: 1 } },
    capabilities: [{ capability, returns: artifactTypes.blob, lifecycle: 'asynchronous', endpoint }],
  });
}
