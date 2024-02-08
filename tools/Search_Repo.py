## Auto spider project's message. include starts, last update date, etc.
import requests
import pygal
import argparse

from pygal.style import LightColorizedStyle as LCS, LightenStyle as LS

# 创建解析器对象
parser = argparse.ArgumentParser(description='Description of your program')

# 添加命令行参数
# parser.add_argument('filename', type=str, help='Write filename')
# parser.add_argument('input_val', type=str, help='search content')
parser.add_argument('--filename', metavar='filename', type=str, help='Input variable in the format filename')
parser.add_argument('--input_val', metavar='input_val', type=str, help='Input variable in the format input_val')

# 解析命令行参数
args = parser.parse_args()

# 访问解析后的参数
filename = args.filename
input_val = args.input_val

print(" filename =",filename,"\n","input_val =",input_val)

#filename = "../src/AI_ori.md"

# 获取用户输入的变量
#input_val = input("请输入repo名称: ")
#input_val="cnn"
#input_val="cnn AND inference"

# 构建URL并替换变量
URL = 'https://api.github.com/search/repositories?q={}&sort=stars'.format(input_val)

print("url:",URL)

r = requests.get(URL)
print("Status code:",r.status_code)

response_dict = r.json()
print("Total repositories:",response_dict['total_count'])
repo_dicts = response_dict['items']
count = 0

existing_strings = set()  # 存储已经存在的字符串
# 读取文件内容并将已存在的字符串添加到集合中
with open(filename, "r") as file:
    for line in file:
        existing_strings.add(line.strip())

for repo_dict in repo_dicts:
    if count >= 100:
        break
    if repo_dict['stargazers_count'] < 1000:
        continue
    if len(repo_dict['description']) > 1000:
        continue
    repo_string = "[" + repo_dict['full_name'] + "](" + repo_dict['git_url'] + ")"
    if any(existing_string.find(repo_string) != -1 for existing_string in existing_strings):
        print("#####exist string=",repo_string)
        continue
    print("|" + str(repo_dict['stargazers_count']) + "|" + "[" +  repo_dict['full_name'] + "]" + "(" +  repo_dict['git_url'] + ")" + "|" +  repo_dict['language'] + "|" +  repo_dict['description'] + "|" +  repo_dict['updated_at'] + "|" + repo_dict['created_at'])
    with open(filename, "a") as file:
        file.write("|" + str(repo_dict['stargazers_count']) + "|[" + repo_dict['full_name'] + "](" + repo_dict['git_url'] + ")|" + repo_dict['language'] + "|" + repo_dict['description'] + "|" + repo_dict['updated_at'] + "|" + repo_dict['created_at'] + "|\n")
    count += 1
 # 打开文件，使用追加模式（"a"）以便将内容添加到现有文件中，如果文件不存在则创建新文件
