from ada_leval.smp import *
from ada_leval.util import *
from ada_leval.api import OpenAIWrapper
from ada_leval.dataset import StackSelect, TextSort

RESULT_FILE = 'result.json'
if not osp.exists(RESULT_FILE):
    dump({}, RESULT_FILE)

settings = ['1k', '2k', '4k', '8k', '16k', '32k', '64k', '128k']
datasets = [f'stackselect_{k}' for k in settings] + [f'textsort_{k}' for k in settings]

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=str, nargs='+', required=True, choices=datasets)
    parser.add_argument('--model', type=str, required=True, choices=['internlm2-7b', 'internlm2-20b', 'gpt-4-0125'])
    parser.add_argument('--mode', type=str, default='all', choices=['infer', 'all'])
    parser.add_argument('--nproc', type=int, default=4)
    args = parser.parse_args()
    return args

def build_model(m):
    if m == 'gpt-4-0125':
        model = OpenAIWrapper('gpt-4-0125-preview')
    return model

import tiktoken
ENC = tiktoken.encoding_for_model('gpt-4')

def get_token_length(prompt):
    return len(ENC.encode(prompt))

def main():
    os.makedirs('results', exist_ok=True)
    args = parse_args()
    model_name = args.model
    model = build_model(args.model)
    for dname in args.data:
        d, setting = dname.split('_')
        dataset_mode = 'less' if model.is_api else 'normal'

        if d == 'stackselect':
            dataset = StackSelect(setting=setting, mode=dataset_mode)
        else:
            dataset = TextSort(setting=setting, mode=dataset_mode)

        lt = len(dataset)
        prompts = [dataset.build_prompt(i) for i in range(lt)]
        meta = dataset.get_meta()
        indices = list(meta['index'])
        
        out_file = f'results/{model_name}_{dname}.pkl'
        res = {} if not osp.exists(out_file) else load(out_file)
        tups = [(i, p) for i, p in zip(indices, prompts) if i not in res]
        
        if len(tups):
            if model.is_api:
                res = track_progress_rich(
                    model.generate, 
                    [x[1] for x in tups], 
                    nproc=args.nproc, 
                    chunksize=args.nproc, 
                    save=out_file, 
                    keys=[x[0] for x in tups])
            else:
                pass

        res = load(out_file)
        meta['prediction'] = [res[k] for k in meta['index']]
        dump(meta, f'results/{model_name}_{dname}.xlsx')

        if args.mode == 'all':
            results = load(RESULT_FILE)
            acc = dataset.evaluate(meta)
            results[f'{model_name}_{dname}'] = acc
            dump(results, RESULT_FILE)

if __name__ == '__main__':
    main()