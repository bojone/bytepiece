# 共享模型

在38G中英混合语料（中英比为3:5）上训练的两个模型：

|  | vocab size | 压缩率 (bytes/token) |
| :----: | :----: | :----: |
| [bytepiece_80k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece_80k.zip) | 79,896 | 5.09 |
| [bytepiece_160k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece_160k.zip) | 159,896 | 5.34 |

在185G混合语料（中、英、代码语料比为3:5:0.5）上训练的模型：

|  | vocab size | 压缩率 (bytes/token) |
| :----: | :----: | :----: |
| [bytepiece.plus.40k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.plus.40k.zip) | 39,843 | 4.63 |
| [bytepiece.plus.80k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.plus.80k.zip) | 79,812 | 5.13 |
| [bytepiece.plus.160k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.plus.160k.zip) | 159,846 | 5.56 |
| [bytepiece.plus.240k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.plus.240k.zip) | 239,858 | 5.74 |
| [bytepiece.plus.320k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.plus.320k.zip) | 319,768 | 5.83 |
| [bytepiece.id.plus.40k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.id.plus.40k.zip) | 39,857 | 4.51 |
| [bytepiece.id.plus.80k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.id.plus.80k.zip) | 79,827 | 4.96 |
| [bytepiece.id.plus.160k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.id.plus.160k.zip) | 159,868 | 5.34 |
| [bytepiece.id.plus.240k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.id.plus.240k.zip) | 239,888 | 5.50 |
| [bytepiece.id.plus.320k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.id.plus.320k.zip) | 319,808 | 5.58 |
| [bytepiece.eu.plus.40k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.eu.plus.40k.zip) | 39,842 | 4.59 |
| [bytepiece.eu.plus.80k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.eu.plus.80k.zip) | 79,816 | 5.11 |
| [bytepiece.eu.plus.160k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.eu.plus.160k.zip) | 159,831 | 5.57 |
| [bytepiece.eu.plus.240k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.eu.plus.240k.zip) | 239,862 | 5.76 |
| [bytepiece.eu.plus.320k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.eu.plus.320k.zip) | 319,767 | 5.86 |
| [bytepiece.id.eu.plus.40k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.id.eu.plus.40k.zip) | 39,857 | 4.65 |
| [bytepiece.id.eu.plus.80k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.id.eu.plus.80k.zip) | 79,829 | 5.08 |
| [bytepiece.id.eu.plus.160k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.id.eu.plus.160k.zip) | 159,869 | 5.41 |
| [bytepiece.id.eu.plus.240k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.id.eu.plus.240k.zip) | 239,884 | 5.55 |
| [bytepiece.id.eu.plus.320k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece.id.eu.plus.320k.zip) | 319,811 | 5.61 |

其中id指的是isolate digits，即将阿拉伯数字单独分开；eu指的是eusure unicode，保证每一个多字节token都可以decode为unicode。可以看到，在固定的语料配比上，当vocab_size到大一定程度后，增大vocab_size也无法带来明显的压缩率提高。
