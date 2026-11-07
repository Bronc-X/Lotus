import { resolve } from 'node:path';
import { createRuntimeEndpointAdapterFacet, runtimeConfigExact, runtimeConfigObject, runtimeConfigPositiveInteger, runtimeConfigString } from '@hypit/hypit/runtime-kit';
import { manifest, component, surfaceFacet } from './author.mjs';
import { createKlingUiProvider } from './provider.mjs';
export default {
  format: 'hypit.node-package@1', modules: [{ manifest }], components: [component],
  hostFacets: [surfaceFacet, createRuntimeEndpointAdapterFacet({
    use: '@portrait/kling-ui', activate(context) {
      const config = runtimeConfigObject(context.config, 'Kling UI bridge');
      runtimeConfigExact(config, ['exchangeRoot', 'pollIntervalMs'], 'Kling UI bridge');
      const directory = runtimeConfigString(config.exchangeRoot, 'exchangeRoot');
      if (!directory || !context.pool) throw new Error('Kling UI bridge requires exchangeRoot and pool');
      return { endpoint: createKlingUiProvider({ instance: context.instance, pool: context.pool,
        exchangeRoot: resolve(context.dataRoot, directory), pollIntervalMs: runtimeConfigPositiveInteger(config.pollIntervalMs, 'pollIntervalMs') ?? 5000,
      }) };
    },
  })],
};
