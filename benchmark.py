
"""
ChemInformant vs. PubChemPy
(285 unique drugs x 6 properties)

Output:
  • PubChemPy bulk time
  • ChemInformant first-call batch time (cold)
  • ChemInformant cache-hit batch time (warm, mean of 3 runs)
  • Throughput (compounds / s) and speed-up ratios
"""


import statistics
import time
import uuid

import pubchempy as pcp

import ChemInformant as ci

# ---------------- 1. 285 unique drug names ----------------
DRUGS = sorted({
    "abacavir","acetaminophen","acetazolamide","acyclovir","adalimumab",
    "albendazole","albuterol","alclometasone","allopurinol","alprazolam",
    "amiodarone","amitriptyline","amlodipine","amoxicillin","ampicillin",
    "anastrozole","apixaban","aripiprazole","aspirin","atorvastatin",
    "azathioprine","azithromycin","baclofen","beclomethasone","benzene",
    "betamethasone","bisoprolol","bortezomib","brinzolamide","budesonide",
    "bupivacaine","bupropion","cabergoline","capecitabine","capsaicin",
    "carbamazepine","carboplatin","carvedilol","cefazolin","cefepime",
    "ceftriaxone","celecoxib","cephalexin","chloramphenicol","chloroquine",
    "chlorpromazine","cilostazol","ciprofloxacin","cisplatin","clindamycin",
    "clobetasol","clonazepam","clopidogrel","clozapine","colchicine",
    "cyclobenzaprine","cyclophosphamide","cyclosporine","dapagliflozin",
    "daptomycin","darunavir","dasatinib","desloratadine","dexamethasone",
    "dexmedetomidine","diazepam","diclofenac","digoxin","diltiazem",
    "diphenhydramine","disulfiram","docetaxel","donepezil","dopamine",
    "dorzolamide","doxycycline","dronedarone","duloxetine","efavirenz",
    "enalapril","epinephrine","erlotinib","esomeprazole","estradiol",
    "ethambutol","etoposide","everolimus","exemestane","famciclovir",
    "famotidine","felodipine","fenofibrate","fentanyl","ferrous sulfate",
    "finasteride","fluconazole","fludarabine","fludrocortisone","flumazenil",
    "fluoxetine","fluticasone","folic acid","foscarnet","fosfomycin",
    "furosemide","gabapentin","ganciclovir","gemcitabine","gefitinib",
    "glimepiride","glipizide","glucose","glyburide","haloperidol",
    "heparin sodium","hydralazine","hydrochlorothiazide","hydrocodone",
    "hydrocortisone","hydromorphone","ibandronate","ibuprofen","idarubicin",
    "ifosfamide","imatinib","indomethacin","insulin","interferon alfa-2b",
    "ipratropium","irbesartan","irinotecan","isavuconazole","isoniazid",
    "isotretinoin","itraconazole","ketamine","ketoconazole","ketoprofen",
    "ketorolac","lamivudine","lamotrigine","lansoprazole","leflunomide",
    "lenalidomide","leuprolide","levofloxacin","levothyroxine","lidocaine",
    "linagliptin","lisinopril","lithium carbonate","loratadine","losartan",
    "lovastatin","mafenide","magnesium sulfate","mebendazole","medroxyprogesterone",
    "meloxicam","meropenem","mesalamine","metformin","methadone",
    "methotrexate","methyldopa","metoclopramide","metoprolol","metronidazole",
    "miconazole","midazolam","milrinone","minocycline","mirtazapine",
    "mitoxantrone","montelukast","morphine","mycophenolate","nabumetone",
    "nadolol","nalbuphine","naloxone","naproxen","nelfinavir",
    "neomycin","nicardipine","nicotine","nifedipine","nitazoxanide",
    "nitrofurantoin","nitroglycerin","norepinephrine","norfloxacin","octreotide",
    "ofloxacin","olanzapine","omeprazole","ondansetron","oseltamivir",
    "oxaliplatin","oxazepam","oxycodone","oxymorphone","paclitaxel",
    "pantoprazole","paracetamol","paroxetine","pazopanib","penicillin G",
    "pentazocine","pentobarbital","phenazopyridine","phenobarbital","phenytoin",
    "pioglitazone","piperacillin","pravastatin","prednisone","pregabalin",
    "primidone","probenecid","prochlorperazine","progesterone","promethazine",
    "propofol","propranolol","pyrazinamide","quetiapine","quinapril",
    "quinidine","rabeprazole","raltegravir","ramipril","ranitidine",
    "ribavirin","rifampicin","rilpivirine","risperidone","ritonavir",
    "rivastigmine","rosuvastatin","salbutamol","sertraline","sildenafil",
    "simvastatin","sirolimus","sitagliptin","spironolactone","stavudine",
    "streptomycin","sucralfate","sulfadiazine","sulfamethoxazole","sumatriptan",
    "sunitinib","tacrolimus","tamoxifen","temazepam","temozolomide",
    "terbinafine","terbutaline","testosterone","tetracycline","thiopental",
    "ticagrelor","tigecycline","tizanidine","tolterodine","topiramate",
    "torsemide","tramadol","trazodone","trimethoprim","valacyclovir",
    "valproic acid","vancomycin","varenicline","venlafaxine","verapamil",
    "vinblastine","vincristine","voriconazole","warfarin","zidovudine",
    "zolpidem","zonisamide"
})

API_TAGS = [
    "MolecularWeight","MolecularFormula","XLogP",
    "CanonicalSMILES","IsomericSMILES","IUPACName"
]

# ---------------- 2. resolve name ➜ CID  (not timed) ----------------
good_cids, skipped = [], []
for n in DRUGS:
    try:
        good_cids.append(ci.cheminfo_api._resolve_to_single_cid(n))
    except Exception:
        skipped.append(n)
print(f"Resolved {len(good_cids)} / {len(DRUGS)} names "
      f"(skipped {len(skipped)})")

# ---------------- 3. ChemInformant  cold / warm ---------------------
ci.setup_cache(cache_name=f"ci_{uuid.uuid4().hex}",
               backend="sqlite", expire_after=3600)

t0 = time.perf_counter()
ci.api_helpers.get_batch_properties(good_cids, API_TAGS)
ci_cold = time.perf_counter() - t0

warm_times = []
for _ in range(3):
    t0 = time.perf_counter()
    ci.api_helpers.get_batch_properties(good_cids, API_TAGS)
    warm_times.append(time.perf_counter() - t0)
ci_warm = statistics.mean(warm_times)

# ---------------- 4. PubChemPy bulk baseline ------------------------
t0 = time.perf_counter()
pcp.get_properties(API_TAGS, good_cids, namespace="cid")
pcp_time = time.perf_counter() - t0

# ---------------- 5. report ----------------------------------------
def rate(s): return len(good_cids) / s

print(f"\nNetwork-only timings ({len(good_cids)} CIDs × 6 props)")
print(f"{'Method':26}{'Time (s)':>10}{'Throughput':>15}")
print(f"{'PubChemPy bulk':26}{pcp_time:10.2f}{rate(pcp_time):15.0f}")
print(f"{'CI cold batch':26}{ci_cold:10.2f}{rate(ci_cold):15.0f}")
print(f"{'CI warm cache (avg)':26}{ci_warm:10.3f}{rate(ci_warm):15.0f}")

print("\nSpeed-ups")
print(f"  CI-cold  vs PCP : ×{pcp_time/ci_cold:4.1f}")
print(f"  CI-warm vs cold : ×{ci_cold/ci_warm:4.0f}")
print(f"  CI-warm vs PCP  : ×{pcp_time/ci_warm:7.0f}")

print(f"\n*Batch completed in **{ci_cold:.1f} s** vs "
      f"**{pcp_time:.0f} s** for PubChemPy "
      f"({pcp_time/ci_cold:.1f}×). Cached re-query returned in "
      f"**{ci_warm*1e3:.0f} ms** "
      f"({ci_cold/ci_warm:.0f}× over cold, {pcp_time/ci_warm:.0f}× over baseline).*")
