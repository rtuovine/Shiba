import numpy as np
import os
from argparse import ArgumentParser
from dataclasses import dataclass
from scipy import linalg, special, sparse, constants

def parser():
   parser = ArgumentParser(description="Script to comput Yu-Shiba-Rusinov states")
   parser.add_argument("-input", "--input",
                        type=str,
                        required=True,
                        help="""Input file to execute Shiba""")
   
   parser.add_argument("-outdir", "--outdir",
                        type=str,
                        required=False,
                        default='',
                        help="Path to store the outputs")
   
   args = parser.parse_args()
   return args.input, args.outdir

@dataclass
class ParameterManager: 
      #Input parameters (Default values)
      mu: float = 0.0                # Fermi level in eV
      temperature: float = 350.0e-3  # 
      delta: float = 0.0  # Superconductive pair potential (phenomenological) in eV
      alpha: float = 0.0  # Spin-orbit interaction (phenomenological parameter) in ???
      gamma: float = 0.1e-3  # Coupling strength of the electrodes (estimated from peak width) in eV          
      frac: float = 1.0      # Relative coupling: sub vs stm (1.0 means equal coupling).
      vran: float = 5.0e-1   # Voltage range in eV
      vpts: int = 1000       # Number of voltage points
      nc: int = 0            # Number of Wigner-Seitz neigbouring cells considered for the overlaps in the supermatrix
      spec: int = 0          # Calculate spectral and transmision functions
      opt: int = 2           # Optimization
      plot: bool = True      # Make plots?
      up_nstm: np.ndarray = np.array([])
      down_nstm: np.ndarray = np.array([])
      up_nsub: np.ndarray = np.array([])
      down_nsub: np.ndarray = np.array([])
      comb_nstm: np.ndarray = np.array([])
      comb_nsub: np.ndarray = np.array([])

      # Files
      input_dir: str = ''
      outdir: str = ''
      shiba_input: str = ''
      up_h: str = ''
      down_h: str = ''
      comb_h: str = ''
      up_stm: str = ''
      down_stm: str = ''
      up_sub: str = ''
      down_sub: str = ''
      comb_stm: str = ''
      comb_sub: str = ''

      # Constants
      EVTOA: float = constants.eV**2/constants.hbar
      BETA: float = 100.0
      
      def extract_input_information(self) -> None:
          shiba_input_and_dir, self.outdir = parser()
          self.input_dir = os.path.abspath(os.path.dirname(shiba_input_and_dir))
          self.shiba_input = os.path.basename(shiba_input_and_dir)
          if self.outdir == '':
             self.outdir = self.input_dir
          input_file = open(os.path.join(self.input_dir,self.shiba_input), 'r')
          checkcomb=True
          for line_number, line in enumerate(input_file): 
            splitted_line = line.replace('\n','').replace(' ','').replace(',','').split('='); 
            if len(splitted_line) > 1:
               if splitted_line[0].lower() == 'up_stm_file':
                  self.up_stm = splitted_line[1]
                  checkcomb=False
               if splitted_line[0].lower() == 'down_stm_file':
                  self.down_stm = splitted_line[1]
               if splitted_line[0].lower() == 'up_sub_file':
                  self.up_sub = splitted_line[1]
               if splitted_line[0].lower() == 'down_sub_file':
                  self.down_sub = splitted_line[1]
               if splitted_line[0].lower() == 'comb_stm_file':
                  self.comb_stm = splitted_line[1]
                  checkcomb=True
               if splitted_line[0].lower() == 'comb_sub_file':
                  self.comb_sub = splitted_line[1]
               if splitted_line[0].lower() == 'up_h':
                  self.up_h = splitted_line[1]
               if splitted_line[0].lower() == 'down_h':
                  self.down_h = splitted_line[1]
               if splitted_line[0].lower() == 'comb_h':
                  self.comb_h = splitted_line[1]
               if splitted_line[0].lower() == 'mu':
                  self.mu = float(splitted_line[1])
               if splitted_line[0].lower() == 'delta':
                  self.delta = float(splitted_line[1])
               if splitted_line[0].lower() == 'temperature':
                  self.temperature = float(splitted_line[1])
               if splitted_line[0].lower() == 'alpha':
                  self.alpha = float(splitted_line[1])
               if splitted_line[0].lower() == 'gamma':
                  self.gamma = float(splitted_line[1])
               if splitted_line[0].lower() == 'frac':
                  self.frac = float(splitted_line[1])
               if splitted_line[0].lower() == 'vran':
                  self.vran = float(splitted_line[1])
               if splitted_line[0].lower() == 'vpts':
                  self.vpts = int(splitted_line[1])
               if splitted_line[0].lower() == 'nc': 
                  self.nc = int(splitted_line[1])
               if splitted_line[0].lower() == 'opt': 
                  self.opt = int(splitted_line[1])
               if splitted_line[0].lower() == 'spec':  
                  if splitted_line[1] in '0yY' or splitted_line[1].lower()== 'true': 
                     self.spec = 0
                  elif splitted_line[1] in '1nN' or splitted_line[1].lower()== 'false':
                     self.spec = 1
               if splitted_line[0].lower() == 'plot':  
                  if splitted_line[1] in '0yY' or splitted_line[1].lower()== 'true': 
                     self.plot = True
                  elif splitted_line[1] in '1nN' or splitted_line[1].lower()== 'false':
                     self.plot = False
          self.BETA = 1.0/((constants.k/constants.eV)*self.temperature)
          if(checkcomb):
             self.comb_nstm = np.loadtxt(os.path.join(self.input_dir,self.comb_stm),dtype=int,ndmin=1)
             self.comb_nsub = np.loadtxt(os.path.join(self.input_dir,self.comb_sub),dtype=int,ndmin=1)
          else:
             self.up_nstm = np.loadtxt(os.path.join(self.input_dir,self.up_stm),dtype=int,ndmin=1)
             self.down_nstm = np.loadtxt(os.path.join(self.input_dir,self.down_stm),dtype=int,ndmin=1)
             self.up_nsub = np.loadtxt(os.path.join(self.input_dir,self.up_sub),dtype=int,ndmin=1)
             self.down_nsub = np.loadtxt(os.path.join(self.input_dir,self.down_sub),dtype=int,ndmin=1)

