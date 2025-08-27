import React, { useState, useEffect } from 'react';
import { Box, Flex, VStack, HStack, Heading, Text, Button, Input, Select, Checkbox, NumberInput, NumberInputField, NumberInputStepper, NumberInputIncrementStepper, NumberInputDecrementStepper, Table, Thead, Tbody, Tr, Th, Td, Card, CardBody, useToast, FormControl, FormLabel, Textarea } from '@chakra-ui/react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, LineChart, Line, ResponsiveContainer } from 'recharts';
import dayjs from 'dayjs';

interface Lancamento {
  id: number;
  data: string;
  entrada: string;
  saida_almoco: string;
  volta_almoco: string;
  saida: string;
  observacao: string;
  valido: boolean;
}

interface Config {
  carga_horaria_diaria_min: number;
  entrada_padrao: string;
  saida_padrao: string;
  almoco_padrao_min: number;
  considerar_ausencia_como_debito: boolean;
  dias_uteis: string[];
  arredondamento_min: number | null;
}

interface Periodo {
  tipo: 'dia' | 'semana' | 'mes' | 'intervalo';
  inicio: string;
  fim: string;
}

interface Resumo {
  total_trabalhado_min: number;
  total_esperado_min: number;
  saldo_min: number;
  media_por_dia_min: number;
}

interface Serie {
  data: string;
  saldo_min: number;
}

interface Props {
  config: Config;
  periodo: Periodo;
  lancamentos: Lancamento[];
  resumo: Resumo;
  series: {
    saldo_diario: Serie[];
    saldo_acumulado: Serie[];
  };
}

const App: React.FC = () => {
  const [props, setProps] = useState<Props | null>(null);
  const [selectedDate, setSelectedDate] = useState(dayjs().format('YYYY-MM-DD'));
  const [formData, setFormData] = useState({
    entrada: '',
    saida_almoco: '',
    volta_almoco: '',
    saida: '',
    observacao: ''
  });
  const toast = useToast();

  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data.type === 'streamlit:setComponentValue') {
        setProps(event.data.value);
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  const sendEvent = (action: string, payload: any) => {
    window.parent.postMessage({
      type: 'streamlit:setComponentValue',
      value: { action, payload }
    }, '*');
  };

  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
  };

  const parseTime = (time: string) => {
    const [h, m] = time.split(':').map(Number);
    return h * 60 + m;
  };

  const handleSubmit = () => {
    const lancamento = {
      data: selectedDate,
      entrada: formData.entrada,
      saida_almoco: formData.saida_almoco,
      volta_almoco: formData.volta_almoco,
      saida: formData.saida,
      observacao: formData.observacao
    };
    sendEvent('create', lancamento);
    setFormData({ entrada: '', saida_almoco: '', volta_almoco: '', saida: '', observacao: '' });
    toast({ title: 'Lançamento criado', status: 'success', duration: 2000 });
  };

  const handleDelete = (id: number) => {
    sendEvent('delete', { id });
    toast({ title: 'Lançamento deletado', status: 'success', duration: 2000 });
  };

  if (!props) return <Text>Carregando...</Text>;

  return (
    <Flex direction="column" h="100vh">
      <HStack spacing={4} p={4} bg="gray.100">
        <FormControl>
          <FormLabel>Data</FormLabel>
          <Input type="date" value={selectedDate} onChange={(e) => setSelectedDate(e.target.value)} />
        </FormControl>
        <FormControl>
          <FormLabel>Entrada</FormLabel>
          <Input type="time" value={formData.entrada} onChange={(e) => setFormData({ ...formData, entrada: e.target.value })} />
        </FormControl>
        <FormControl>
          <FormLabel>Saída Almoço</FormLabel>
          <Input type="time" value={formData.saida_almoco} onChange={(e) => setFormData({ ...formData, saida_almoco: e.target.value })} />
        </FormControl>
        <FormControl>
          <FormLabel>Volta Almoço</FormLabel>
          <Input type="time" value={formData.volta_almoco} onChange={(e) => setFormData({ ...formData, volta_almoco: e.target.value })} />
        </FormControl>
        <FormControl>
          <FormLabel>Saída</FormLabel>
          <Input type="time" value={formData.saida} onChange={(e) => setFormData({ ...formData, saida: e.target.value })} />
        </FormControl>
        <FormControl>
          <FormLabel>Observação</FormLabel>
          <Textarea value={formData.observacao} onChange={(e) => setFormData({ ...formData, observacao: e.target.value })} />
        </FormControl>
        <Button colorScheme="blue" onClick={handleSubmit}>Salvar</Button>
      </HStack>
      <Flex flex={1}>
        <VStack w="300px" p={4} bg="gray.50" spacing={4}>
          <Heading size="md">Configurações</Heading>
          <FormControl>
            <FormLabel>Carga Diária (min)</FormLabel>
            <NumberInput value={props.config.carga_horaria_diaria_min} onChange={(valueString) => sendEvent('set_config', { ...props.config, carga_horaria_diaria_min: parseInt(valueString) })}>
              <NumberInputField />
              <NumberInputStepper>
                <NumberInputIncrementStepper />
                <NumberInputDecrementStepper />
              </NumberInputStepper>
            </NumberInput>
          </FormControl>
          <FormControl>
            <FormLabel>Entrada Padrão</FormLabel>
            <Input type="time" value={props.config.entrada_padrao} onChange={(e) => sendEvent('set_config', { ...props.config, entrada_padrao: e.target.value })} />
          </FormControl>
          <FormControl>
            <FormLabel>Saída Padrão</FormLabel>
            <Input type="time" value={props.config.saida_padrao} onChange={(e) => sendEvent('set_config', { ...props.config, saida_padrao: e.target.value })} />
          </FormControl>
          <FormControl>
            <FormLabel>Almoço Padrão (min)</FormLabel>
            <NumberInput value={props.config.almoco_padrao_min} onChange={(valueString) => sendEvent('set_config', { ...props.config, almoco_padrao_min: parseInt(valueString) })}>
              <NumberInputField />
              <NumberInputStepper>
                <NumberInputIncrementStepper />
                <NumberInputDecrementStepper />
              </NumberInputStepper>
            </NumberInput>
          </FormControl>
          <Checkbox isChecked={props.config.considerar_ausencia_como_debito} onChange={(e) => sendEvent('set_config', { ...props.config, considerar_ausencia_como_debito: e.target.checked })}>
            Considerar ausência como débito
          </Checkbox>
          <FormControl>
            <FormLabel>Dias Úteis</FormLabel>
            {['seg', 'ter', 'qua', 'qui', 'sex'].map(day => (
              <Checkbox key={day} isChecked={props.config.dias_uteis.includes(day)} onChange={(e) => {
                const newDias = e.target.checked ? [...props.config.dias_uteis, day] : props.config.dias_uteis.filter(d => d !== day);
                sendEvent('set_config', { ...props.config, dias_uteis: newDias });
              }}>
                {day}
              </Checkbox>
            ))}
          </FormControl>
          <FormControl>
            <FormLabel>Arredondamento (min)</FormLabel>
            <Select value={props.config.arredondamento_min || ''} onChange={(e) => sendEvent('set_config', { ...props.config, arredondamento_min: e.target.value ? parseInt(e.target.value) : null })}>
              <option value="">Nenhum</option>
              <option value="5">5</option>
              <option value="10">10</option>
              <option value="15">15</option>
            </Select>
          </FormControl>
          <Button onClick={() => sendEvent('export_csv', {})}>Exportar CSV</Button>
        </VStack>
        <VStack flex={1} p={4} spacing={4}>
          <HStack spacing={4}>
            <Card>
              <CardBody>
                <Text>Total Trabalhado: {formatTime(props.resumo.total_trabalhado_min)}</Text>
              </CardBody>
            </Card>
            <Card>
              <CardBody>
                <Text>Total Esperado: {formatTime(props.resumo.total_esperado_min)}</Text>
              </CardBody>
            </Card>
            <Card>
              <CardBody>
                <Text>Saldo: {formatTime(props.resumo.saldo_min)}</Text>
              </CardBody>
            </Card>
            <Card>
              <CardBody>
                <Text>Média/Dia: {formatTime(props.resumo.media_por_dia_min)}</Text>
              </CardBody>
            </Card>
          </HStack>
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>Data</Th>
                <Th>Entrada</Th>
                <Th>Saída Almoço</Th>
                <Th>Volta Almoço</Th>
                <Th>Saída</Th>
                <Th>Trabalhado</Th>
                <Th>Saldo</Th>
                <Th>Observação</Th>
                <Th>Ações</Th>
              </Tr>
            </Thead>
            <Tbody>
              {props.lancamentos.map(l => (
                <Tr key={l.id}>
                  <Td>{l.data}</Td>
                  <Td>{l.entrada}</Td>
                  <Td>{l.saida_almoco}</Td>
                  <Td>{l.volta_almoco}</Td>
                  <Td>{l.saida}</Td>
                  <Td>{formatTime((parseTime(l.saida_almoco) - parseTime(l.entrada)) + (parseTime(l.saida) - parseTime(l.volta_almoco)))}</Td>
                  <Td>{formatTime((parseTime(l.saida_almoco) - parseTime(l.entrada)) + (parseTime(l.saida) - parseTime(l.volta_almoco)) - props.config.carga_horaria_diaria_min)}</Td>
                  <Td>{l.observacao}</Td>
                  <Td><Button size="sm" colorScheme="red" onClick={() => handleDelete(l.id)}>Deletar</Button></Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
          <Box w="100%" h="300px">
            <ResponsiveContainer>
              <BarChart data={props.series.saldo_diario}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="data" />
                <YAxis />
                <Tooltip formatter={(value: number) => formatTime(value)} />
                <Bar dataKey="saldo_min" fill={(entry: any) => entry.saldo_min >= 0 ? 'green' : 'red'} />
              </BarChart>
            </ResponsiveContainer>
          </Box>
          <Box w="100%" h="300px">
            <ResponsiveContainer>
              <LineChart data={props.series.saldo_acumulado}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="data" />
                <YAxis />
                <Tooltip formatter={(value: number) => formatTime(value)} />
                <Line type="monotone" dataKey="acumulado_min" stroke="#8884d8" />
              </LineChart>
            </ResponsiveContainer>
          </Box>
        </VStack>
      </Flex>
    </Flex>
  );
};

export default App;