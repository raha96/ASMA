# Run with: streamlit run streamlit_project_demo.py

import streamlit as st
import random
import glob
import os
import re

ENABLE_LINE_NUMBERS = True


# Define transformation functions
def remove_comments(input_code: str) -> str:
	out_lines = []
	for line in input_code.splitlines():
		if line.startswith("//"):
			continue
		if line.strip() == "":
			continue
		out_lines.append(line)
	output_code = "\n".join(out_lines)
	output_code = re.sub(r"\/\*.+\*\/", "", output_code)

	return output_code

def normalize_verilog(input_code: str) -> str:
	# TODO: Replace this function with the actual code for normalizing Verilog
	return input_code

def add_description_comments(input_code: str) -> str:
	# TODO: Replace this function with the actual code for adding description comments
	return input_code

def evaluate_quality_score(input_code: str) -> str:
	# TODO: Replace this function with the actual code for evaluating the quality score
	return random.choice(["good", "bad"])


# Define the Streamlit app
def main():
	st.title("Verilog State Machine Transformer and Assessor")

	with st.expander("Example Verilog State Machines for Demo"):
		with open(os.path.join('sample_fsms', 'apbcontrol_2.v'), 'r') as f:
			ex1 = f.read()
		st.code(ex1, language="verilog", line_numbers=ENABLE_LINE_NUMBERS)

	# Input textbox
	st.subheader("Input")
	src_verilog_code = st.text_area("Input a Verilog state machine:", placeholder='Verilog code here')

	# TODO: add copy-able sample code snippets

	if st.button("Transform"):
		st.subheader("Output")
		
		if src_verilog_code:

			with st.expander("Original Verilog Code"):
				st.code(src_verilog_code, language="verilog", line_numbers=ENABLE_LINE_NUMBERS)

			with st.expander("Stage 1: Remove Comments"):
				transformed_code_1 = remove_comments(src_verilog_code)
				st.code(transformed_code_1, language="verilog", line_numbers=ENABLE_LINE_NUMBERS)

			with st.expander("Stage 2: Normalize Verilog"):
				transformed_code_2 = normalize_verilog(transformed_code_1)
				st.code(transformed_code_2, language="verilog", line_numbers=ENABLE_LINE_NUMBERS)

			with st.expander("Stage 3: Add Description Comments"):
				transformed_code_3 = add_description_comments(transformed_code_2)
				st.code(transformed_code_3, language="verilog", line_numbers=ENABLE_LINE_NUMBERS)

			# Quality score (randomly classify as "good" or "bad")
			quality_score = evaluate_quality_score(transformed_code_3)
			col1, col2, col3, col4 = st.columns(4)
			col1.metric(label="Quality Score", value=quality_score)
			col2.metric(label="Character Count", value=len(src_verilog_code))
			col3.metric(label="Word Count", value=src_verilog_code.count(' ')) # FIXME
			col4.metric(label="Token Count", value=random.randint(10, 100)) # FIXME

if __name__ == "__main__":
	main()
