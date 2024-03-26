from ada_leval.smp import *
from ada_leval.util import *
from ada_leval.api import OpenAIWrapper
from ada_leval.dataset import StackSelect


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
    args = parse_args()
    model_name = args.model
    model = build_model(args.model)
    for dname in args.data:
        d, setting = dname.split('_')
        dataset_mode = 'less' if model.is_api else 'normal'

        if d == 'stackselect':
            dataset = StackSelect(setting=setting, mode=dataset_mode)
        else:
            pass

        lt = len(dataset)
        prompts = [dataset.build_prompt(i) for i in range(lt)]
        meta = dataset.get_meta()
        indices = list(meta['index'])
        
        out_file = f'{model_name}_{dname}.pkl'
        res = {} if not osp.exists(out_file) else load(res)
        tups = [(i, p) for i, p in zip(indices, prompts) if i not in res]
        
        if model.is_api:
            res = track_progress_rich(
                model.generate, 
                [x[1] for x in tups], 
                nproc=args.nproc, 
                chunksize=args.nproc, 
                save=out_file, 
                key=[x[0] for x in tups])
        else:
            pass
        res = load(out_file)
        meta['prediction'] = [res[k] for k in meta['index']]
        dump(meta, f'{model_name}_{dname}.xlsx')

        if args.mode == 'all':
            # Do the evaluation

if __name__ == '__main__':
    main()