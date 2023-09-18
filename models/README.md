# 共享模型

在38G中英混合语料（中英比为3:5）上训练的两个模型：

|  | vocab size | 压缩率 (bytes/token) |
| :----: | :----: | :----: |
| [bytepiece_80k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece_80k.zip) | 79,896 | 5.09 |
| [bytepiece_160k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece_160k.zip) | 159,896 | 5.34 |

在185G混合语料（中、英、代码语料比为3:5:0.5）上训练的五个模型：

|  | vocab size | 压缩率 (bytes/token) |
| :----: | :----: | :----: |
| [bytepiece.plus.40k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.plus.40k.zip) | 39,843 | 4.63 |
| [bytepiece.plus.80k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.plus.80k.zip) | 79,812 | 5.13 |
| [bytepiece.plus.160k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.plus.160k.zip) | 159,846 | 5.56 |
| [bytepiece.plus.240k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.plus.240k.zip) | 239,858 | 5.74 |
| [bytepiece.plus.320k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.plus.320k.zip) | 319,768 | 5.83 |

可以看到，在固定的语料配比上，当vocab_size到大一定程度后，增大vocab_size也无法带来明显的压缩率提高。
