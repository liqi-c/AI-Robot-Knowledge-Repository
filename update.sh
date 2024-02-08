#/bin/sh 


#python3 ./tools/get_ai_ori.py /home/qli/Data/WorK_Dir/Axera/Code/github_project/AI-Robot-Knowledge-Repository/src/AI_ori.md cnn
python3 ./tools/Search_Repo.py --filename ./src/AI_ori.md --input_val cnn

python3 ./tools/Search_Repo.py --filename ./src/AI_ori.md --input_val "cnn And Inference"
python3 ./tools/Search_Repo.py --filename ./src/AI_ori.md --input_val "Tengine AND cnn"
python3 ./tools/Search_Repo.py --filename ./src/AI_ori.md --input_val "mnn&cnn"


python3 ./tools/Search_Repo.py --filename ./src/AI_llm.md --input_val llm

python3 ./tools/Search_Repo.py --filename ./src/AI_aigc.md --input_val aigc

