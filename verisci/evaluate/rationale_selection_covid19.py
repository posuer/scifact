"""
Computes the rationale selection F1 as in the paper. In order for a sentence to
be correctly identified as a rationale sentence, all other sentences in its gold
rationale must be identified as well.
"""


import argparse
import jsonlines
from collections import Counter
import os
from lib.metrics import compute_f1


def is_correct(pred_sentence, pred_sentences, gold_sets):
    """
    A predicted sentence is correctly identified if it is part of a gold
    rationale, and all other sentences in the gold rationale are also
    predicted rationale sentences.
    """
    # for gold_set in gold_sets:
    #     gold_sents = gold_set["sentences"]
    if pred_sentence in gold_sets:
        if all([x in pred_sentences for x in gold_sets]):
            return True
        else:
            return False

    return False


parser = argparse.ArgumentParser()
#parser.add_argument('--corpus', type=str, required=True)
parser.add_argument('--dataset', type=str, required=True)
parser.add_argument('--rationale-selection', type=str, required=True)
parser.add_argument('--deleting-model-path', type=str, default=None, required=False)
parser.add_argument('--deleting-model-threshold', type=float, default=0.0, required=False)

args = parser.parse_args()


#corpus = {doc['cord_id']: doc for doc in jsonlines.open(args.corpus)}
dataset = jsonlines.open(args.dataset)
rationale_selection = jsonlines.open(args.rationale_selection)

counts = Counter()


for data, retrieval in zip(dataset, rationale_selection):
    assert data['id'] == retrieval['claim_id']

    # Count all the gold evidence sentences.
    # for doc_key, gold_rationales in data["evidence"].items():
    #     for entry in gold_rationales:
    #         counts["relevant"] += len(entry["sentences"])
    counts["relevant"] += len(data["evidence_set"])

    claim_id = retrieval['claim_id']

    for doc_id, pred_sentences in retrieval['evidence'].items():
        #true_evidence_sets = data['evidence'].get(doc_id) or []
        true_evidence_sets = [evd_id_list["sent_index"] for evd_id_list in data['evidence_set']]

        for pred_sentence in pred_sentences:
            counts["retrieved"] += 1
            if is_correct(pred_sentence, pred_sentences, true_evidence_sets):
                counts["correct"] += 1

f1 = compute_f1(counts)
print(f1)


#remove the evaluated model for space saving
if args.deleting_model_path and f1["f1"] < args.deleting_model_threshold:
    if os.path.exists(args.deleting_model_path):
        for root, subdirs, files in os.walk(args.deleting_model_path):
            for file in files:
                os.remove(os.path.join(root, file))
        os.rmdir(args.deleting_model_path)
