from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContractForm, CounterpartyForm
from .models import Contract, Counterparty


@login_required
def contract_list(request):
    contracts = Contract.objects.prefetch_related("parties")
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    if query:
        contracts = contracts.filter(
            Q(contract_number__icontains=query)
            | Q(title__icontains=query)
            | Q(parties__name__icontains=query)
        ).distinct()
    if status in Contract.Status.values:
        contracts = contracts.filter(status=status)
    return render(
        request,
        "contracts/contract_list.html",
        {"contracts": contracts, "query": query, "status": status, "statuses": Contract.Status.choices},
    )


@login_required
def contract_detail(request, pk):
    contract = get_object_or_404(Contract.objects.prefetch_related("parties"), pk=pk)
    return render(request, "contracts/contract_detail.html", {"contract": contract})


@login_required
@atomic
def contract_create(request):
    form = ContractForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        contract = form.save()
        return redirect("contracts:detail", pk=contract.pk)
    return render(request, "contracts/contract_form.html", {"form": form, "heading": "Tạo hợp đồng"})


@login_required
@atomic
def contract_update(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    form = ContractForm(request.POST or None, instance=contract)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("contracts:detail", pk=contract.pk)
    return render(request, "contracts/contract_form.html", {"form": form, "heading": "Cập nhật hợp đồng"})


@login_required
def counterparty_list(request):
    parties = Counterparty.objects.all()
    return render(request, "contracts/counterparty_list.html", {"parties": parties})


@login_required
def counterparty_create(request):
    form = CounterpartyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("contracts:parties")
    return render(request, "contracts/counterparty_form.html", {"form": form})
