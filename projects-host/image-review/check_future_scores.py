"""Apply the NAS's current learned cutoff to future scores from the SAME scorer.
Input: JSON list of {sha256,score}, where score is rank_score from refinement v1.
Output: suggestions only; this never changes or moves images or saved decisions.
"""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from owner_request import open_owner

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args()
    if args.output.exists():parser.error('Output already exists; choose a new output path.')
    rows=json.loads(args.input.read_text(encoding='utf-8-sig'))
    if not isinstance(rows,list) or not rows:parser.error('Input must be a nonempty JSON list.')
    results=[];threshold=None
    for i in range(0,len(rows),2500):
        with open_owner('/image-review/api/learning/predict','POST',{'score_schema':'mungoon-refinement-rank-v1','items':rows[i:i+2500]}) as response:
            batch=json.load(response)
        if threshold is not None and threshold != batch['threshold']:raise RuntimeError('Filter changed during checks. Retry; no output written.')
        threshold=batch['threshold'];results.extend(batch['items'])
    with args.output.open('x',encoding='utf-8') as output:
        json.dump({'score_schema':'mungoon-refinement-rank-v1','threshold':threshold,'items':results,'original_images_modified':False},output,indent=2)
    print('Checked',len(results),'scores. Suggestions saved to',args.output)

if __name__=='__main__':main()
