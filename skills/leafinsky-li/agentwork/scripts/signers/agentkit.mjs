import { pathToFileURL } from 'node:url';

function unavailable(message = 'agentkit signer requires @coinbase/agentkit and configured CDP credentials') {
  throw new Error(message);
}

export const provider = 'agentkit';
export const signerType = 'agentkit-managed';
export const requiresKeystore = false;

function resolveAgentkitSpecifier() {
  const override = process.env.AGENTWORK_AGENTKIT_MODULE?.trim();
  if (!override) return '@coinbase/agentkit';
  if (override.startsWith('.') || override.startsWith('/')) {
    return pathToFileURL(override).href;
  }
  return override;
}

async function loadAgentkit() {
  try {
    return await import(resolveAgentkitSpecifier());
  } catch {
    unavailable();
  }
}

function resolveNetworkId(opts) {
  return opts?.meta?.networkId ?? opts?.networkId ?? process.env.NETWORK_ID ?? 'base-mainnet';
}

function resolvePersistedAddress(meta) {
  if (typeof meta?.address === 'string' && /^0x[a-fA-F0-9]{40}$/.test(meta.address)) {
    return meta.address;
  }
  if (typeof meta?.walletId === 'string' && /^0x[a-fA-F0-9]{40}$/.test(meta.walletId)) {
    return meta.walletId;
  }
  return null;
}

function resolvePrimaryType(types, preferredPrimaryType) {
  if (typeof preferredPrimaryType === 'string' && preferredPrimaryType.length > 0) {
    return preferredPrimaryType;
  }
  if (!types || typeof types !== 'object') return undefined;
  const entries = Object.keys(types).filter((key) => key !== 'EIP712Domain');
  return entries[0];
}

async function configureWalletProvider(opts = {}) {
  const agentkit = await loadAgentkit();
  if (!agentkit?.CdpEvmWalletProvider?.configureWithWallet) {
    unavailable('agentkit signer requires CdpEvmWalletProvider from @coinbase/agentkit');
  }

  return await agentkit.CdpEvmWalletProvider.configureWithWallet({
    apiKeyId: process.env.CDP_API_KEY_ID,
    apiKeySecret: process.env.CDP_API_KEY_SECRET,
    walletSecret: process.env.CDP_WALLET_SECRET,
    networkId: resolveNetworkId(opts),
    ...(resolvePersistedAddress(opts.meta) ? { address: resolvePersistedAddress(opts.meta) } : {}),
    ...(process.env.RPC_URL ? { rpcUrl: process.env.RPC_URL } : {}),
  });
}

export async function createWallet(opts) {
  const networkId = resolveNetworkId(opts);
  const wallet = await configureWalletProvider({ ...opts, meta: null, networkId });
  const exported = typeof wallet.exportWallet === 'function' ? await wallet.exportWallet() : null;
  const address = typeof exported?.address === 'string'
    ? exported.address
    : (typeof wallet.getAddress === 'function' ? wallet.getAddress() : null);
  if (!address) {
    unavailable('agentkit signer could not resolve created wallet address');
  }

  return {
    address,
    meta: {
      address,
      networkId,
      ...(typeof exported?.name === 'string' && exported.name.length > 0 ? { walletName: exported.name } : {}),
    },
  };
}

export async function loadWallet(opts) {
  const persistedAddress = resolvePersistedAddress(opts.meta);
  if (!persistedAddress) {
    unavailable('agentkit signer requires wallet metadata with address for wallet recovery');
  }

  const wallet = await configureWalletProvider({
    ...opts,
    meta: {
      ...opts.meta,
      address: persistedAddress,
    },
  });

  return {
    address: typeof wallet.getAddress === 'function' ? wallet.getAddress() : persistedAddress,
    wallet,
  };
}

export async function signMessage(opts) {
  const { wallet } = await loadWallet(opts);
  return {
    signature: await wallet.signMessage(opts.message),
  };
}

export async function signTypedData(opts) {
  const { wallet } = await loadWallet(opts);
  return {
    signature: await wallet.signTypedData({
      domain: opts.domain,
      types: opts.types,
      primaryType: resolvePrimaryType(opts.types, opts.primaryType),
      message: opts.message,
    }),
  };
}

export async function getAddress(opts) {
  const { address } = await loadWallet(opts);
  return { address };
}
