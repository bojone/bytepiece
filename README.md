[中文|[English](https://github.com/bojone/bytepiece/blob/main/README_en.md)]

# BytePiece
BytePiece是一个Byte-based的Unigram分词器，纯Python实现，更加易读和易拓展。由于采用了新的训练算法，所以压缩率通常比现有Tokenizer更高，同时支持多进程加速训练。此外，它直接操作文本的UTF-8 Bytes，几乎不进行任何的预处理，所以更加纯粹和语言无关。

博客：
- https://kexue.fm/archives/9752
- https://kexue.fm/archives/9768

## 性质

理想的Tokenizer及其训练算法，应该具备以下特点：
- 无损重构
- 高压缩率
- 语言无关
- 数据驱动
- 训练友好

目前主流的[SentencePiece](https://github.com/google/sentencepiece)，事实上已经基本具备以上特性，但仍存在一些问题。比如：它支持BPE和Unigram两种算法，BPE压缩率往往更高一些，但训练极慢，而且非常耗内存；它还是对文本进行了少许语言相关的预处理的，所以“语言无关”这一点也不够纯粹。此外，它是用C++写的，对于多数用户来说就是黑箱，因此也不利于研究和修改。

BytePiece构思了新的基于 **Byte-based N-gram Language Model（BNLM）** 的训练方式，能获得更高压缩率的词表，同时支持多进程训练，同等语料下相比SentencePiece的BPE训练有明显的加速。代码是纯Python，方便大家阅读和二次修改。此外，BytePiece还提供了比[Subword Regularization](https://arxiv.org/abs/1804.10959)更加高效的随机分词算法。

## 原理

BytePiece并非单纯基于Byte-based和多进程来重写已有的Unigram模型，而是为Unigram设计了新的训练方案，这是它压缩率更高的关键原因之一。

新的训练方案基于N-gram语言模型的新词发现算法，首次提出于笔者7年前的博客[《【中文分词系列】 5. 基于语言模型的无监督分词》](https://kexue.fm/archives/3956)，细节请移步阅读。

至于新的随机分词算法，则可以参考[《随机分词浅探：从Viterbi Decoding到Viterbi Sampling》](https://kexue.fm/archives/9768)和[《随机分词再探：从Viterbi Sampling到完美采样算法》](https://kexue.fm/archives/9811)。

## 安装

BytePiece只能运行在Python3上，使用了[pyahocorasick](https://github.com/WojciechMula/pyahocorasick)来加速训练过程。由于BytePiece是Byte-based的，而PyPi上的pyahocorasick是Unicode-based的，所以不能直接用，需要参考如下方式安装Byte-based版的pyahocorasick：
```bash
# 如果已经安装，请先卸载
pip uninstall pyahocorasick

# 直接从git编译安装，注意要传入环境变量AHOCORASICK_BYTES
AHOCORASICK_BYTES=1 pip install git+https://github.com/WojciechMula/pyahocorasick.git
```
然后安装Cython：
```bash
pip install Cython
```
安装完之后，就可以用pip安装BytePiece了：
```bash
pip install bytepiece==0.5.0
```

## 使用

BytePiece的所有源码其实也就是单文件，包含`Trainer`和`Tokenizer`两个类，分别对应训练和分词。

### 训练

训练Tokenizer只需要引入`Trainer`类：
```python
from bytepiece import Trainer
```
然后准备训练语料。BytePiece支持不一次性将所有语料读进内存中，但由于BytePiece训练需要过两遍数据，所以不支持Generator输入，而是要写成Iterator的形式，例如：
```python
import json

class corpus:
    def __iter__(self):
        f = 'data_sample.json'
        with open(f) as f:
            for l in f:
                yield json.loads(l)['text']  # 每次返回一个Unicode
```
然后就可以正式训练了：
```python
trainer = Trainer(order=6, max_vocab_size=100000, min_count=32)
trainer.train(corpus(), workers=64, batch_size=1000)
trainer.save('bytepiece.model')
```
这里的`order`就是n-gram语言模型的阶，推荐默认`order=6`就好；`max_vocab_size`是词表最大尺寸，注意由于去冗的原因，最后得到的词表不一定精确等于max_vocab_size，而是有可能会略少于；`min_count`则是token最低出现频数，数据量大时可以适当调大，一般不会明显影响训练结果；`workers`是并行训练的进程数，可以跑满机器的所有核心；`batch_size`是批大小，不会影响训练结果，一般情况下不用改，如果发现CPU利用率不满可以适当调大。

### 分词

训练完成后，参考使用方式：
```python
from bytepiece import Tokenizer

tokenizer = Tokenizer('bytepiece.model')
text = '今天天气不错'

tokens = tokenizer.tokenize(text)  # 返回bytes的list
print(b' '.join(tokens).decode(errors='ignore'))  # 可视化分词结果

ids = tokenizer.encode(text)  # 返回tokens对应的ids
print(tokenizer.decode(ids))  # 重新将ids解码为unicode文本

tokens = tokenizer.tokenize(text, alpha=0.2)  # 随机tokenize
print(b' '.join(tokens).decode(errors='ignore'))  # 可视化分词结果
```

## 对比

小数据量对比：

|  | 训练时间↓ | 最大内存占用↓ | 压缩率↑ | 分词速度↑ |
| :----: | :----: | :----: | :----: | :----: |
| SP-BPE | 55.3分钟 | 5.2GB | 4.80 | 5.47 |
| SP-Unigram | 1.6分钟 | 2.5GB | 4.73 | 7.84 |
| BytePiece | 6.5分钟 | 4.3GB | 5.05 | 2.50 |

大数据量对比：

|  | 训练时间↓ | 最大内存占用↓ | 压缩率(同源)↑ | 压缩率(异源)↑ | 分词速度↑ |
| :----: | :----: | :----: | :----: | :----: | :----: |
| SP-BPE | 19.21小时 | 97GB | 4.52 | 4.46 | 1.27 |
| SP-Unigram | 2.02小时 | 384GB | 4.51 | 4.48 | 5.55 |
| BytePiece | 2.24小时 | 51GB | 5.39 | 4.51 | 1.92 |

压缩率的单位是“bytes/token”，即平均每个token对应的字节数；速度的单位是“M bytes/second”，即平均每秒可以切分的字节数（以百万为单位）。其他细节请参考[这里](https://kexue.fm/archives/9752#%E6%95%88%E6%9E%9C%E6%B5%8B%E8%AF%95)。

第一个表格的数据集平均长度较短，BytePiece同时慢于SP-BPE和SP-Unigram；在第二个表格中，语料的平均长度普遍更长，出现了BytePiece的速度优于SP-BPE的结果。这说明BPE的分词速度受长度影响比较明显，也说明经过Cython加速的BytePiece分词速度，速度上已经可以跟SentencePiece相比较。

## 下载

在38G中英混合语料（中英比为3:5）上训练的两个模型：

|  | vocab size | 压缩率 (bytes/token) |
| :----: | :----: | :----: |
| [bytepiece_80k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece_80k.zip) | 79,896 | 5.09 |
| [bytepiece_160k](https://github.com/bojone/bytepiece/blob/main/models/bytepiece_160k.zip) | 159,896 | 5.34 |

在185G混合语料（中、英、代码语料比为3:5:0.5）上训练的五个模型（内存峰值519GB，耗时27.7小时）：

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

其中id指的是isolate digits，即将阿拉伯数字单独分开。可以看到，在固定的语料配比上，当vocab_size到大一定程度后，增大vocab_size也无法带来明显的压缩率提高。

## 引用

```
@misc{bytepiece2023,
  title={BytePiece: A more pure and effective tokenizer},
  author={Jianlin Su},
  year={2023},
  howpublished={\url{https://github.com/bojone/bytepiece}},
}
```

## 交流
QQ群：67729435，微信群请加机器人spaces_ac_cn

