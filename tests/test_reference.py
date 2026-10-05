import unittest
import numpy as np
from dmqc_lab.reference import exact_lower_bound,measure_binary_particles,qualify
class ReferenceTests(unittest.TestCase):
    def test_exact_bound_known_all_successes(self):
        self.assertAlmostEqual(exact_lower_bound(150,150),.05**(1/150),places=12)
        self.assertLess(exact_lower_bound(150,150,5),.98)
    def test_small_or_non_independent_is_not_confirmation(self):
        self.assertEqual(qualify({'successes':10,'independent_cases':10})['status'],'pending')
    def test_count_validation(self):
        for args in ((2,1),(0,0),(1.5,2),(True,2)):
            with self.assertRaises(ValueError): exact_lower_bound(*args)
    def test_missing_calibration_suspends(self):
        self.assertEqual(measure_binary_particles(np.zeros((3,3)))['status'],'suspended')
    def test_calibrated_area_and_disconnected_objects(self):
        a=np.zeros((6,6),dtype=np.uint8); a[0:2,0:2]=255; a[4:6,4:6]=255
        self.assertEqual(measure_binary_particles(a,2)['areas_nm2'],[16,16])
    def test_invalid_calibration(self):
        for value in (0,-1,float('nan'),True):
            with self.assertRaises(ValueError): measure_binary_particles(np.zeros((2,2)),value)
if __name__=='__main__': unittest.main()
