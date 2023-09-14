'''

This code calculates current-voltage characteristics of a molecular structure 
coupled to wide bandwidth electrodes. The molecular structure is described by 
Wannier orbitals (input data from Wannier90) and Nambu spinor representation. 
The current is obtained from the Landauer-Büttiker formula via an efficient 
calculation of nonequilibrium Green's functions. The code can read spinful 
(one cmd line argument for input file) and spin-resolved (two cmd line arguments 
for the spin-down and spin-up input files) Wannier input data. The code can be 
used to study, for instance, magnetic molecular effects in the vicinity of a 
superconductor, such as Yu-Shiba-Rusinov states as in-gap conductance peaks.

Example runs

CrBr3-NbSe2 (single Wannier input):
python3 wstm.py crbr3.nbse2.bilayer_hr.dat

Fe-NbSe2 (separate Wannier input for spin-down and spin-up):
python3 wstm.py nbse2.down_hr.dat nbse2.up_hr.dat

riku.m.s.tuovinen@jyu.fi
dorye.esteras@uv.es

'''

from Shiba.wannier_reader import WannierHamiltonian
from Shiba.basic_functions import logger,get_time,stop_watch,estimate_memory
from Shiba.parameter_manager import parser, ParameterManager
from Shiba.transport_calculations import TransportCalculation
from Shiba.plotter import PlotManager
import time





if __name__ == '__main__':
   start = time.time()

   logfile = 'out.log'  
   open(logfile, 'w').close()

   Parameters = ParameterManager()
   Parameters.extract_input_information()
   WannierParameters = WannierHamiltonian()
   WannierParameters.read_wannier_info(Parameters)

   estimate_memory(Parameters,WannierParameters)
   
   TransportHamiltonian = TransportCalculation()
   TransportHamiltonian.construct_nambu(Parameters,WannierParameters)
   TransportHamiltonian.construct_coupling_matrices(Parameters,WannierParameters)
   TransportHamiltonian.solve_hamiltonian(Parameters)
   Plotter = PlotManager()
   Plotter.manage_plots(Parameters,TransportHamiltonian)
    
####################
# Timer and finish #
####################

logger('\n')
logger('Done! ' + stop_watch(start, time.time()) + '\n')

