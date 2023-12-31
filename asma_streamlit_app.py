# Run with: streamlit run streamlit_project_demo.py

import streamlit as st
import random
import glob
import os
import re
from asma_predict import predict_str

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


# Define the Streamlit app
def main():
	st.title("Automated State Machine Auditor")

	with st.expander("Example Verilog Code for Demo"):
		with open(os.path.join('sample', 'gptsample.v'), 'r') as f:
			ex1 = f.read()
		st.code(ex1, language="verilog", line_numbers=ENABLE_LINE_NUMBERS)

	# Input textbox
	st.subheader("Input")
	src_verilog_code = st.text_area("Input a Verilog state machine:", placeholder='Verilog code here')

	# TODO: add copy-able sample code snippets

	if st.button("Audit"):
		st.subheader("Output")
		
		if src_verilog_code:

			with st.expander("Original Verilog Code"):
				st.code(src_verilog_code, language="verilog", line_numbers=ENABLE_LINE_NUMBERS)

			#with st.expander("Stage 1: Remove Comments"):
			#	transformed_code_1 = remove_comments(src_verilog_code)
			#	st.code(transformed_code_1, language="verilog", line_numbers=ENABLE_LINE_NUMBERS)
			#
			#with st.expander("Stage 2: Normalize Verilog"):
			#	transformed_code_2 = normalize_verilog(transformed_code_1)
			#	st.code(transformed_code_2, language="verilog", line_numbers=ENABLE_LINE_NUMBERS)
			#
			#with st.expander("Stage 3: Add Description Comments"):
			#	transformed_code_3 = add_description_comments(transformed_code_2)
			#	st.code(transformed_code_3, language="verilog", line_numbers=ENABLE_LINE_NUMBERS)

			# Quality score (randomly classify as "good" or "bad")
			#quality_score = evaluate_quality_score(transformed_code_3)
			#col1, col2, col3, col4 = st.columns(4)
			#col1.metric(label="Quality Score", value=quality_score)
			#col2.metric(label="Character Count", value=len(src_verilog_code))
			#col3.metric(label="Word Count", value=src_verilog_code.count(' ')) # FIXME
			#col3.metric(label="Token Count", value=random.randint(10, 100)) # FIXME
			
			# Run the model
			results = predict_str(src_verilog_code)

			# Display some basic info
			col_len, col_toks, col_fsm = st.columns(3)
			col_len.metric(label="Character Count", value=len(src_verilog_code))
			col_toks.metric(label="Token Count", value=results["token_count"])
			col_fsm.metric(label="Contains FSM", value="Yes" if results["hasfsm"] else "No")

			# Display the main predictions
			col_q, col_label, col_sens, col_trans = st.columns(4)
			col_q.metric(label="Overal quality", value="Good" if results["good"] else "Bad")
			col_label.metric(label="States labeled", value="Yes" if results["labeled"] else "No")
			col_sens.metric(label="Sensitivity list", value="Good" if results["sensitivity"] else "No")
			col_trans.metric(label="Separated transitions", value="Yes" if results["transitions"] else "No")

			st.divider()
			num_hints = 0
			if not results["hasfsm"]:
				st.write("The provided source code might not contain any state machine, so take these hints with a grain of salt.")
				num_hints += 1
			if results["good"]:
				st.write("The general style is good. Well done!")
				num_hints += 1
			if not results["labeled"]:
				st.write("Labeling the states makes the code more readable.")
				num_hints += 1
			if not results["sensitivity"]:
				st.write("The sensitivity lists would benefit from being better written and more understandable. ")
				num_hints += 1
			if not results["transitions"]:
				st.write("Separating state transitions from output generation makes the code more readable. ")
				num_hints += 1
			if num_hints == 0:
				st.write("We haven't got any hints for you right now, pal.")

if __name__ == "__main__":
	main()
