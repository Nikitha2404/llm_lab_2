from src.pkg.resume_query import analyse_resume,llmstats
from src.utils.logging import setup_logging
import json
import difflib
from dotenv import load_dotenv
import os

load_dotenv()

basepath = os.getenv("BASE_DIR_PATH")

def get_outputs(fileName):
    with open(basepath+"/resume_data/output/"+fileName+".jsonl") as f1, open(basepath+"/resume_data/eval/"+fileName+".jsonl") as f2:
        got_output = [json.loads(line) for line in f1]
        expected_output = [json.loads(line) for line in f2]
    return got_output, expected_output

def normalize_text(s):
    return s.lower().strip()

def soft_match_string(got, expected):
    if expected == None:
        return 1.0 if got in ["",None,"N/A","null","Not specified"] else 0.0
    else:
        seq_match = difflib.SequenceMatcher(None,normalize_text(got),normalize_text(expected))
        return seq_match.ratio()

def match_numbers(got, expected,tolerance=0):
    if expected == None:
        return 1.0 if got in ["",None,"N/A","null","Not specified"] else 0.0
    try:
        got = float(got)
        expected = float(expected)
        diff = abs(got - expected)
        if diff <= tolerance:
            return 1.0
        else:
            return max(0.0, 1.0 - (diff / max(expected, 1)))
    except:
        return 0.0

def fuzzy_list_match(got_list, expected_list, threshold=0.85):
    if not got_list and not expected_list:
        return 1.0  # perfect match if both are empty
    
    got_list = [normalize_text(x) for x in got_list or []]
    expected_list = [normalize_text(x) for x in expected_list or []]

    matches = 0
    used = set() # To get O(1) lookup time for used indices
    for expected in expected_list:
        best_score = 0
        best_match = None
        # Find the best match for the current expected string
        for i, got in enumerate(got_list):
            if i in used:
                continue
            score = difflib.SequenceMatcher(None, got, expected).ratio()
            if score > best_score:
                best_score = score
                best_match = i
        # If a match is found >= threshold, mark it as used in the got_list
        if best_score >= threshold:
            matches += 1
            used.add(best_match)
    return matches / max(len(got_list), len(expected_list))  # overlap ratio

def compare_entries(got, expected):
    result = {}
    result["candidate_name"] = soft_match_string(got["candidate_name"], expected["candidate_name"])
    result["education_level"] = soft_match_string(got["education_level"], expected["education_level"])
    result["current_job_role"]=soft_match_string(got["current_job_role"], expected["current_job_role"])
    result["skills"]=fuzzy_list_match(got["skills"], expected["skills"])
    result["projects_count"]=match_numbers(got["projects_count"], expected["projects_count"])
    result["experience_years"]=match_numbers(got["experience_years"], expected["experience_years"])
    print(result)

def evaluation(inputFileName):
    setup_logging(output_dir=basepath)
    analyse_resume(
        inputfilePath=basepath+"/resume_data/input/"+inputFileName+".csv",
        outputfilePath=basepath+"/resume_data/output/"+inputFileName+".jsonl"
    )
    llmstats.log_summary()
    got_output, expected_output = get_outputs(inputFileName)
    results=[]
    for got,expected in zip(got_output,expected_output):
        result=compare_entries(got,expected)
        results.append(result)
    return results

evaluation("test_list")

