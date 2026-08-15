# DR-02 Revision 2 — Model and Pricing Verification Snapshot

**Verification date:** 2026-08-15  
**Purpose:** Preserve the official-source facts used to frame DR-02 revision 2. This evidence record does not freeze final model revisions or authorize spending.

## Verified model records

### Qwen

- [`Qwen/Qwen3.5-9B-Base`](https://huggingface.co/Qwen/Qwen3.5-9B-Base) is an official pretrained-only checkpoint intended for fine-tuning, in-context experiments, and research.
- [`Qwen/Qwen3.6-27B`](https://huggingface.co/Qwen/Qwen3.6-27B) is an official post-trained checkpoint. It must not be treated as a clean Base model.
- No unverified Qwen3.8 open-weight model identity is frozen into DR-02. Any later official release must pass the current-release audit required by DR-11.

### Gemma

- [`google/gemma-4-12B`](https://huggingface.co/google/gemma-4-12B) is an official pretrained Gemma 4 12B checkpoint; a matched instruction-tuned variant is published separately.
- [`google/gemma-4-31B`](https://huggingface.co/google/gemma-4-31B) is an official pretrained Gemma 4 31B checkpoint; a matched instruction-tuned variant is published separately.
- The official model records describe Gemma 4 as multimodal, long-context, and multilingual. Project-specific suitability remains unproven until the approved bake-off.

### Ministral

- [`mistralai/Ministral-3-8B-Base-2512`](https://huggingface.co/mistralai/Ministral-3-8B-Base-2512) is an official Base checkpoint.
- [`mistralai/Ministral-3-8B-Instruct-2512`](https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512) is an official instruction-tuned variant.
- [`mistralai/Ministral-3-8B-Reasoning-2512`](https://huggingface.co/mistralai/Ministral-3-8B-Reasoning-2512) is an official reasoning variant.

## Verified Lambda on-demand price snapshot

The official [Lambda pricing page](https://lambda.ai/pricing) listed the following self-service prices on the verification date:

| Instance configuration | Listed price |
|---|---:|
| 4× H100 SXM | $4.09 per GPU-hour; $16.36 per node-hour |
| 8× H100 SXM | $3.99 per GPU-hour; $31.92 per node-hour |
| 2× B200 SXM6 | $6.89 per GPU-hour; $13.78 per node-hour |
| 1× B200 SXM6 | $6.99 per hour |
| 1× GH200 | $2.29 per hour |
| 1× H100 PCIe | $3.29 per hour |

These prices are informational only. DR-25 requires live price verification and a separate immutable campaign approval before every billable run.

## Evidence limitations

- Vendor benchmark results are not evidence of superiority on Biblical Scholar Lab tasks.
- Model cards may change after this snapshot.
- Exact repository and tokenizer revisions remain deferred to DR-11.
- The $300–$700 Gemma bake-off range is a project planning estimate, not a Lambda quote.
