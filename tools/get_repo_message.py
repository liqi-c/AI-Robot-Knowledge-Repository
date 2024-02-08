## Auto spider project's message. include starts, last update date, etc.
import requests
import pygal
from pygal.style import LightColorizedStyle as LCS, LightenStyle as LS

# 获取用户输入的变量
input_var = input("请输入repo名称: ")
# 构建URL并替换变量
URL = 'https://api.github.com/search/repositories?q={}&sort=stars'.format(input_var)

print("url:",URL)

r = requests.get(URL)
print("Status code:",r.status_code)

response_dict = r.json()
print("Total repositories:",response_dict['total_count'])
repo_dicts = response_dict['items']
names,stars = [],[]
count = 0
for repo_dict in repo_dicts:
 if count >= 100:
  break
 if repo_dict['stargazers_count'] < 1000:
  continue
 if len(repo_dict['description']) > 1000:
  continue
 print("|",repo_dict['stargazers_count'],"|","[", repo_dict['full_name'],"]","(", repo_dict['git_url'],")","|", repo_dict['language'],"|", repo_dict['description'],"|", repo_dict['updated_at'],"|",repo_dict['created_at'])
 count += 1