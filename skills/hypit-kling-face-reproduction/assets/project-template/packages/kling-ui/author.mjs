import { artifactTypes } from '@hypit/hypit/artifact';
import { textTypes } from '@hypit/hypit/text';
import { canonicalize, createMarkupSurfaceHostFacet, sealGraphFragment, sameType } from '@hypit/hypit/author-kit';

export const moduleRef = { name: '@portrait/kling-ui', version: '1' };
export const capability = { module: moduleRef, name: 'edit-video-through-kling-ui' };
export const identityPorts = ['front', 'left45', 'right45', 'left90', 'right90'];
const producer = { module: moduleRef, name: 'request-kling-ui-five-view-edit' };
const inputNames = ['source', 'sourceUpload', ...identityPorts, 'prompt'];
const inputPorts = inputNames.map(name => ({ name, type: name === 'prompt' ? textTypes.text : artifactTypes.blob }));
export const manifest = {
  format: 'hypit.module@1', name: moduleRef.name, version: moduleRef.version,
  dependencies: [{ module: artifactTypes.blob.module }, { module: textTypes.text.module }],
  types: [], capabilities: [{ name: capability.name, returns: artifactTypes.blob }],
  producers: [{ name: producer.name, inputs: inputPorts, outputs: [],
    needs: [{ name: 'video', capability, returns: artifactTypes.blob }],
  }],
};
const fragment = sealGraphFragment({
  inputs: inputPorts,
  operations: [{ id: 'edit', producer,
    inputs: Object.fromEntries(inputNames.map(name => [name, { kind: 'fragment-input', name }])),
    result: { kind: 'need', name: 'video' },
  }],
  exports: [{ name: 'video', type: artifactTypes.blob, root: { kind: 'fragment-operation', operation: 'edit' } }],
});
function requestFrom(inputs) {
  const source = inputs.source?.value, sourceUpload = inputs.sourceUpload?.value, prompt = inputs.prompt?.value;
  if (source?.kind !== 'blob' || !source.mediaType.startsWith('video/')) throw new Error('Source must be a video artifact');
  if (sourceUpload?.kind !== 'blob' || !sourceUpload.mediaType.startsWith('video/')) throw new Error('sourceUpload must be a video artifact');
  if (prompt?.kind !== 'inline' || typeof prompt.value?.value !== 'string' || !prompt.value.value.trim()) throw new Error('Prompt must contain text');
  const identities = identityPorts.map(port => {
    const artifact = inputs[port]?.value;
    if (artifact?.kind !== 'blob' || !artifact.mediaType.startsWith('image/')) throw new Error(`Identity port ${port} must contain an image artifact`);
    return { port, artifact, personReference: true };
  });
  return canonicalize({ source, sourceUpload, sourcePersonReference: true, uploadVideoPersonReference: true, identities, prompt: prompt.value.value });
}
export const component = {
  producers: [{ producer, handler: ({ inputs }) => ({ outputs: {}, needs: { video: requestFrom(inputs) } }) }],
  plannedNeeds: [{ producer, port: 'video', capability,
    plan({ state, step }) {
      const owner = state.plan.steps.find(item => item.id === step);
      if (!owner) return undefined;
      const inputs = Object.fromEntries(Object.entries(owner.inputs).map(([name, id]) => [name, state.records.find(item => item.id === id)]));
      const pendingInputs = Object.entries(owner.inputs).filter(([name]) => !inputs[name]).map(([input, record]) => ({ input, record, role: ['source', 'sourceUpload'].includes(input) ? 'video' : input === 'prompt' ? 'text' : 'image' }));
      return { constraints: pendingInputs.length ? {} : requestFrom(inputs), pendingInputs };
    },
    present({ constraints }) { return { fields: { service: ['Kling browser UI'], identityPorts, videoRoles: ['original for timing/audio', 'compatible upload copy'], ...(constraints.prompt ? { prompt: [constraints.prompt] } : {}) }, references: { video: 2, image: 5 } }; },
  }],
};
const surface = {
  name: 'five-view-video-edit', tag: 'FiveViewVideoEdit', mode: 'structured', outputs: [artifactTypes.blob],
  vocabulary: { summary: 'Queues an original-video edit using five independent target-identity photographs.',
    attributes: [
      { name: 'id', kind: 'identifier', required: true, summary: 'Output name.' },
      ...['source', 'sourceUpload', ...identityPorts].map(name => ({ name, kind: 'reference', required: true, accepts: [artifactTypes.blob], summary: name === 'source' ? 'Original video.' : name === 'sourceUpload' ? 'Compatible copy of the same video for UI upload.' : `Target identity photograph: ${name}.` })),
      { name: 'prompt', kind: 'reference', required: true, accepts: [textTypes.text], summary: 'Requested edit.' },
    ], ports: [{ name: 'video', type: artifactTypes.blob, summary: 'Downloaded edit admitted to this Build.' }],
    example: '<kling:FiveViewVideoEdit id="edit" source={original} sourceUpload={upload} front={front} left45={left45} right45={right45} left90={left90} right90={right90} prompt={direction}/>',
  },
};
export const surfaceFacet = createMarkupSurfaceHostFacet({ module: moduleRef, declaration: surface,
  handler({ element, resolveReference }) {
    if (Object.keys(element.attributes).some(name => !['id', ...inputNames].includes(name))) throw new Error('Unknown FiveViewVideoEdit attribute');
    if (element.children.some(item => item.kind === 'element' || item.value.trim())) throw new Error('FiveViewVideoEdit must be empty');
    const id = element.attributes.id;
    if (typeof id !== 'string' || !id.trim()) throw new Error('FiveViewVideoEdit requires id');
    const inputs = {};
    for (const name of inputNames) {
      const raw = element.attributes[name];
      const resolved = typeof raw === 'object' && raw.kind === 'reference' ? resolveReference(raw.path) : undefined;
      if (!resolved || !sameType(resolved.type, name === 'prompt' ? textTypes.text : artifactTypes.blob)) throw new Error(`Invalid ${name} reference`);
      inputs[name] = resolved.ref;
    }
    return { records: [], fragments: [fragment], components: [{ id, fragment: fragment.id, inputs, outputs: { video: `${id}.video` }, range: element.range }] };
  },
});
