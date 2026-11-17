# 企业能源披露原表采集

本项目接收公开来源的原文及关联记录。当前样例只给出部分证据，未决状态不等于业务事实不存在。

来源响应由 transport 校验，domain 解释资料，ledger 保留事务与版本，view 展示当前证据和缺口。样例为合成资料，不访问真实网站。

在项目根目录执行：

    python -m unittest discover -s tests -v
    python -m compileall -q capture_service tests
    python -m capture_service.cli inspect data/normal.json

Dockerfile 提供 Linux 环境；docker build -t energy-disclosure . 构建，docker run --rm energy-disclosure 运行样例。
