# 纸上版税

出版社发行核算员可用本地工作台处理作者结算单，复查版税分项并与独立清单逐笔核对。

以年初净销量为起点分段计提，退货逆冲最高已占档，再按当期净额和前期准备金结算。

## 启动

```sh
docker compose up --build
```

打开 http://127.0.0.1:18302 并运行随附样例。可以在「导入来源与外部账」上传自己的 CSV，也可以编辑表单中的样例。数据保存于 Compose 卷 `ledger`。使用 `APP_PORT` 可覆盖宿主端口。

## 工作步骤

1. 检查「渠道回执」与「合同字段」，定位导入坏行与字段归一结果。
2. 在「争议结算单」区分冲突、业务拒绝、重传与旧版本。
3. 打开「版税核算」并点击任意记录的「查看依据」。
4. 在「财务勾稽」检查金额或用量差异。通过「月结批次」复算原文件，通过「会签底稿」提交意见并下载证据。

接口定义见 `/openapi.json`。字段、允许区间及算例见 [数据字典](docs/DATA-DICTIONARY.md)，模块和回归测试见 [测试登记](docs/DEPTH.md)。

## 验证

```sh
docker compose config --quiet
docker compose exec -T app pytest -q
```

`sample_data/shift.csv` 是班次数据，`sample_data/external.csv` 是独立账样例。`cases.csv` 固定业务反例，`legacy.csv` 和 `truncated.csv` 用于验证历史格式与断行。
