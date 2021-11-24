import os
from fractions import Fraction
from pysmt_sim.codegen_walker import CodeGenWalker

class CodeGenMgr:

    def __init__(self) -> None:
        self.walker = CodeGenWalker()
        self.patterns = []
        self.file_name = None
        self.args = None

    def gen_code(self, formula, file_name="cpp/tmp.cpp"):
        self.walker.gen_code(formula, file_name)
        self.file_name = file_name
        self.args = self.walker.args

    def compile(self):
        os.system(f"g++ {self.file_name} -o tmp -O3")

    def sim(self, in_file="sim_pattern", out_file="sim_result"):
        self._write_pattern()
        os.system(f"./tmp {in_file} {out_file}")

    def check_allsat(self, out_file="sim_result"):
        with open(out_file, "r") as file:
            for line in file.readlines():
                if line != "1\n":
                    return False
            return True

    def add_pattern(self, patterns: list()):
        for pattern in patterns:
            p_str = {key.symbol_name(): value for key, value in pattern.items()}
            p_tmp = []
            for arg in self.args:
                assert p_str[arg.name].is_constant()
                payload = p_str[arg.name].constant_value()
                if isinstance(payload, Fraction):
                    val = str(payload.numerator / payload.denominator)
                elif isinstance(payload, bool):
                    if payload: val = "1"
                    else: val = "0"
                else:
                    val = str(payload)
                p_tmp.append(val)
            self.patterns.append(p_tmp)

    def clear_pattern(self):
        self.patterns.clear()

    def _write_pattern(self, file_name="sim_pattern"):
        with open(file_name, 'w') as file:
            file.write(f"{len(self.patterns)}\n")
            for pattern in self.patterns:
                file.write(" ".join(pattern) + "\n")
