# 部分数据发布补丁（基于 main ded924e / v2.4.2）

这是小补丁，不是完整仓库；仅调整发布门槛。无需先安装此前 v2.4.3 包。

## GitHub 网页应用
1. 解压本包。
2. 打开仓库 main 分支根目录，Add file → Upload files。
3. 将包内 src 和 tests 两个文件夹拖入上传区，保持原有路径；不要上传 ZIP 或外层文件夹。
4. 确认文件为 src/calendar_status.py、tests/test_v24.py、tests/test_partial_publication.py。提交到 main（或通过 PR 合并）。
5. Actions → Daily Systemic Risk Pipeline → Run workflow → main。
6. 验收：Update available data 的结果为 published:true；Commit and push data 未跳过；data/current.json 指向新 run。
7. 检查对应 data/runs/<run>/latest.json 中 publication.decision=accepted、publication.coverage_policy=advisory，并检查 publication.metric_status 的 as_of/freshness。

## 行为
- 80% 覆盖率只用于告警，不再直接拒绝发布，无需修改仓库变量。
- 候选快照中至少有一家受支持银行的一项有效、有限数值的所选类别指标，才允许继续发布。
- partial 表示未全部达到新鲜度要求；每项指标记录 as_of 和 freshness，缺失项标 unavailable。
- 全空/NaN/Infinity 不能通过；合成或历史数据、未来目标日期、其他质量错误仍会拒绝。
- 原有“快照超过 7 天”等质量规则保留，本包并非取消所有质量检查。
- 完整系统 SRISK 的聚合规则不变。
- 不改变快照按日期组织方式，不将不同日期银行指标伪装成同日数据。旧指标可位于历史文件；publication.metric_status 提供各银行指标的日期。
- 本包不修复 BK ticker、不部署 MCP，也不包含此前 v2.4.3 的其他修复。不能保证外部数据源和线上 MCP 可用。

## 本地测试
python -m pip install '.[test]'
python -m pytest tests/test_partial_publication.py tests/test_v24.py -q

## 回滚
撤销本次提交即可恢复原发布门槛。无需删除历史数据。
