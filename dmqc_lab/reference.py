import math
import numpy as np
from scipy.ndimage import label
from scipy.stats import beta

def exact_lower_bound(successes,total,comparisons=1,alpha=.05):
    if isinstance(successes,bool) or isinstance(total,bool) or not 0<=successes<=total or total<1 or comparisons<1 or not 0<alpha<1: raise ValueError('Invalid confidence-bound inputs')
    if not all(isinstance(x,int) for x in (successes,total,comparisons)): raise ValueError('Counts must be integers')
    return 0.0 if successes==0 else float(beta.ppf(alpha/comparisons,successes,total-successes+1))

def classify_evidence_baseline(state):
    """Declared trivial comparator. Does not solve semantic entailment."""
    return 'NOT_ENOUGH_INFO'

def measure_binary_particles(pixels,pixel_size_nm=None):
    arr=np.asarray(pixels)
    if arr.ndim!=2 or arr.size>4_000_000: raise ValueError('Expected bounded 2D image')
    if pixel_size_nm is None: return {'status':'suspended','reason':'missing_calibration'}
    if isinstance(pixel_size_nm,bool) or not math.isfinite(pixel_size_nm) or pixel_size_nm<=0: raise ValueError('Invalid calibration')
    components,count=label(arr>127)
    areas=[int((components==i).sum()) for i in range(1,count+1)]
    return {'status':'measured','count':count,'areas_px':areas,'areas_nm2':[a*pixel_size_nm**2 for a in areas],'method':'connected_components_synthetic_binary_only'}

def qualify(report):
    required=('configuration_frozen','independent_review','held_out_unseen','critical_violations','successes','independent_cases','comparisons')
    if any(k not in report for k in required): return {'status':'pending','reason':'missing_confirmation_evidence'}
    if report.get('synthetic',True) or report.get('phase')!='confirmation': return {'status':'unqualified','reason':'pilot_or_synthetic'}
    if any(report[k] is not True for k in required[:3]) or report['critical_violations']!=0: return {'status':'unqualified','reason':'confirmation_protocol_not_satisfied'}
    n=report['independent_cases']; s=report['successes']; lower=exact_lower_bound(s,n,report['comparisons'])
    return {'status':'pending_independent_review' if s/n>=.98 and lower>=.98 else 'unqualified','success_rate':s/n,'lower_bound':lower,'note':'Numerical criteria never replace human scientific review.'}
